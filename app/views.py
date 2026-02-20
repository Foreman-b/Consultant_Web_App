from django.shortcuts import render, redirect
from .models import Availability, Booking, User, Payment
from .forms import (
    UserRegisterForm, ConsultantProfileForm,
    AvailabilityForm, BookingForm, PaymentForm, ReviewForm,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone



def home(request):
    return render(request, "app/home.html")


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    
    else:
        form = UserRegisterForm()
    return render(request, 'app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'app/login.html', {'form': form})


def logout_view(request):
    # Let logout the consultant/client and redirects them to the login page
    logout(request)
    return redirect('login')


@login_required
def book_dashboard(request):
    user_bookings = Booking.objects.filter(client=request.user)
    
    # REMOVE .filter(is_booked=False) since the field doesn't exist
    availability_list = Availability.objects.all() 

    context = {
        'user_bookings': user_bookings,
        'availability_list': availability_list,
    }
    return render(request, 'app/book_dashboard.html', context)



@login_required          # let make it only authenticated user can book a session.
def book_session(request, availability_id):

    availability = get_object_or_404(Availability, id=availability_id)
    # Let handle booking session here
    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.availability = availability
            booking.consultant = availability.consultant
            booking.save()
            return redirect("book-dashboard")

    else:
        form = BookingForm()

    return render(request, "app/book_session.html", {"form": form})


@login_required
def consultant_dash(request):
    # Check if the user is a consultant
    if request.user.role == 'CONSULTANT':
        # Option A: Get ALL bookings in the system
        all_bookings = Booking.objects.all().order_by('-created_at')
        
        # Option B: Only get bookings assigned to THIS consultant (if field exists)
        # all_bookings = Booking.objects.filter(consultant=request.user).order_by('-date')
    else:
        # Redirect or handle non-consultants
        all_bookings = []

    return render(request, 'app/consultant_dashboard.html', {'all_bookings': all_bookings})


from django.views.decorators.http import require_POST

@require_POST
@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Optional: Security check to ensure only the consultant can change status
    # if booking.consultant.user != request.user:
    #     return HttpResponseForbidden()

    new_status = request.POST.get('status')
    
    # Check if the submitted status is valid based on your model choices
    if new_status in [choice[0] for choice in Booking.StatusChoices.choices]:
        booking.status = new_status
        booking.save()
        
    return redirect('consultant-dash')


@require_POST
@login_required
def update_meeting_link(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security: Only the assigned consultant can edit this specific booking
    if booking.consultant.user != request.user:
        return redirect('consultant-dash')

    new_link = request.POST.get('meeting_link')
    booking.meeting_link = new_link # Direct assignment to Booking model
    booking.save()
    
    return redirect('consultant-dash')




@login_required
def initialize_payment(request, booking_id):
    # Let fetch booking and confirm the ownership
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        client=request.user,
        status=Booking.Status.Choices.PENDING
    )
    
    # Now let create payment record(server-controlled)
    payment = Payment.objects.create(
        booking =booking,
        amount = 10000,
    )

    # Let prepare Paystack request here
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": payment.amount,
        "reference": str(payment.payment_reference),
        "callback_url": request.build_absolute_url("/verify-payment/"),
    }

    # Right here let call Paystack initialize endpoint
    response = request.post(
        "https://api.paystack.co/transaction/initialize",
        json=data,
        headers=headers,
    )

    response_data = response.json()

    # Let redirect user to Paystack chekout
    return redirect(response_data["data"] ["authorization_url"])


@login_required
def verify_payment(request):
    reference = request.GET.get("reference")

    payment = get_object_or_404(Payment, payment_reference=reference)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    # Let call paystack verify endpoint
    response = request.get(
        f"https://api.paystack.co/transaction/verify/{reference}",

        headers = headers,
    )

    result = response.json()

    if result["data"]["status"] == "success":
        payment.status = Payment.PaymentStatus.SUCCESS
        payment.paid_at = timezone.now()
        payment.save()

        booking = payment.booking
        booking.status = Booking.StatusChoices.CONFIRMED
        booking.save()

    else:
        payment.status = Payment.PaymentStatus.FAILED
        payment.save()

    return redirect("booking-dashboard")