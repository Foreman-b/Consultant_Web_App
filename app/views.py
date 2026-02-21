from django.shortcuts import render, redirect
from .models import Availability, Booking, CustomUser, Payment, Consultant_Profile
from .forms import (
    UserRegisterForm, ConsultantProfileForm, UserUpdateForm,
    AvailabilityForm, BookingForm, PaymentForm, ReviewForm,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
import requests
from django.contrib import messages
import uuid



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
        status=Booking.StatusChoices.PENDING
    )
    
    amount = 500000     # this N5,000.00 in kobo

    # Let create re-usable payment
    payment, create = Payment.objects.get_or_create(
        booking =booking,
        defaults={"amount": amount}
    )

    # Now let prevent user from double payment
    if payment.status == Payment.PaymentStatus.SUCCESS:
        return redirect("book-dashboard")

    # Let handle Paystack API Setup
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Let attempt to initialize
    payload = {
        "email": request.user.email,
        "amount": int(payment.amount),
        "reference": str(payment.payment_reference),
        "callback_url": request.build_absolute_uri("/verify-payment/"),
    }

    # Right here let call Paystack initialize endpoint
    try:
        response = requests.post(
            url, 
            json=payload,
            headers=headers,
        )
        response_data = response.json()
        # print("DEBUG PAYSTACK DATA:", response_data)
        # Let handle duplicate reference
        if not response_data.get("status") and "reference" in response_data.get("message", "").lower():
            #Let it generate new reference and try one more time
            payment.payment_reference = str(uuid.uuid4())
            payment.save()


            payload["reference"] = payment.payment_reference
            response = requests.post(
                url, 
                json=payload,
                headers=headers
            )
            response_data = response.json()
            # print("DEBUG PAYSTACK DATA:", response_data)

            # Let check one time before redirecting
            if response_data.get("status"):
                return redirect(response_data["data"]["authorization_url"])
            else:
                messages.error(request, f"Paystac error: {response_data.get('message')}")   
    except Exception as e:
        messages.error(request, f"Connrection Error: {str(e)}")

    # Let redirect user to Paystack chekout
    return redirect("book-dashboard")


@login_required
def verify_payment(request):
    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "No payment reference found")
        return redirect("book-dashbaord")
    
    # Now let call Paystack to verify the status
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }


    response = requests.get(
        url,
        headers=headers
    )
    response_data = response.json()

    # print("DEBUG PAYSTACK DATA:", response_data)

    if response_data.get("status") and response_data["data"]["status"] == "success":
        
        # Let update the database here
        payment = get_object_or_404(Payment, payment_reference=reference)

        if payment.status != Payment.PaymentStatus.SUCCESS:
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.paid_at = timezone.now()
            payment.save()

            # Now let update the book status
            booking = payment.booking
            booking.status = Booking.StatusChoices.CONFIRMED
            booking.save()

            messages.success(request, "Payment successful! Your Booking is confirmed.")
            return redirect('book-dashboard')
        else:
            messages.error(request, "Payment verification failed. Please contact support.")
    return redirect("book-dashboard")
   


@login_required
def consultant_profile(request):
    user = request.user
    slots = None
    form = None

    # Logic for Consultants
    if user.role == 'CONSULTANT':
        # Let get profile or create one if it doesn't exist (prevents RelatedObjectDoesNotExist)
        profile, created = Consultant_Profile.objects.get_or_create(user=user)
        slots = profile.availabilities.all().order_by('date')
        
        if request.method == 'POST':
            form = ConsultantProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Consultant profile updated!")
                return redirect('profile')
        else:
            form = ConsultantProfileForm(instance=profile)
        
    # Logic for Clients
    elif user.role == 'CLIENT':
        if request.method == 'POST':
            # Basic User form for Clients
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Client settings updated!")
                return redirect('profile')
        else:
            form = UserUpdateForm(instance=user)

    return render(request, 'app/accounts.html', {
        'form': form,
        'slots': slots,
        'user': user
    })

@login_required
def payment_dash(request):
    # Let check if the user is a consultant
    if request.user.role == 'CLIENT':
        # Let bet ALL bookings in the system
        all_payments = Payment.objects.all().order_by('-paid_at')
        all_bookings = Booking.objects.all().order_by('-created_at')

    elif request.user.role == 'CONSULTANT':
        all_payments = Payment.objects.all().order_by('-paid_at')
        all_bookings = Booking.objects.all().order_by('-created_at')
        
    else:
        # Redirect or handle non-consultants
        all_payments, all_bookings = []

    return render(request, 'app/payment_dash.html', {'all_payments': all_payments, 'all_bookings': all_bookings})