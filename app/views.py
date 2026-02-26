from django.shortcuts import render, redirect
from .models import Availability, Booking, CustomUser, Payment, Consultant_Profile, Review
from .forms import (
    UserRegisterForm, ConsultantProfileForm, UserUpdateForm,
    AvailabilityForm, BookingForm, PaymentForm, ReviewForm, 
    AvailabilityFormSet, ClientProfilePicForm, ConsultantProfilePicForm
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
from django.views.decorators.http import require_POST
from django.db.models import Avg
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash



def home(request):
    return render(request, "app/home.html")


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your are successfully registered.")
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
            messages.success(request, "Successfully logged in.")
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out.")
    return redirect('login')


@login_required
def book_dashboard(request):
    user_bookings = Booking.objects.filter(client=request.user)
    
    # Let get availability slot based on recent one by the consultant
    all_slots = Availability.objects.filter(date__gte=timezone.now().date()).order_by('date')

    # Let make dictionary trick that ensures only one slot per consultant is show
    unique_slots = {}
    for slot in all_slots:
        if slot.consultant_id not in unique_slots:
            unique_slots[slot.consultant_id] = slot
            
    availability_list = unique_slots.values()
    
    context = {
        'user_bookings': user_bookings,
        'availability_list': availability_list,
    }
    return render(request, 'app/book_dashboard.html', context)



@login_required       
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
            messages.success(request, "Session successfully booked, click Pay.")
            return redirect("book-dashboard")

    else:
        form = BookingForm()

    return render(request, "app/book_session.html", {"form": form})


@login_required
def consultant_dash(request):
    
    if request.user.role == 'CONSULTANT':
        
        all_bookings = Booking.objects.all().order_by('-created_at')
        avg_rating = Review.objects.filter(
        consultant__user=request.user
        ).aggregate(Avg('rating'))['rating__avg']
        reviews = Review.objects.filter(
        consultant__user=request.user
        ).order_by('-created_at')
        
    else:

        all_bookings = []
        avg_rating = []
        reviews = []

    return render(request, 'app/consultant_dashboard.html', {
        'all_bookings': all_bookings,
        'avg_rating': avg_rating,
        'reviews': reviews,
    })



@require_POST
@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
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
    
    # Only the assigned consultant can edit this specific booking
    if booking.consultant.user != request.user:
        return redirect('consultant-dash')

    new_link = request.POST.get('meeting_link')
    booking.meeting_link = new_link
    booking.save()
    
    return redirect('consultant-dash')




@login_required
def initialize_payment(request, booking_id):

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
        amount= amount,
    )

    # Now let prevent user from double payment
    if payment.status == Payment.PaymentStatus.SUCCESS:
        print("payment has been made")
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

        # print("Response:", response_data)

        # Let check one time before redirecting
        if response_data.get("status"):
            return redirect(response_data["data"]["authorization_url"])
        else:    
            messages.error(request, f"Paystac error: {response_data.get('message')}")   
            return redirect("book-dashboard")
    except Exception as e:

        messages.error(request, f"Connrection Error: {str(e)}")

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
def user_profile(request):
    user = request.user
    slots = None
    form = None

    if user.role == 'CONSULTANT':
        
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
    if request.user.role == 'CLIENT':
        # Get payments for bookings made by this client
        payments = Payment.objects.filter(
            booking__client=request.user
        ).select_related('booking', 'booking__client').order_by('-paid_at')

    elif request.user.role == 'CONSULTANT':
        # Get payments for bookings assigned to this consultant
        payments = Payment.objects.filter(
            booking__availability__consultant__user=request.user
        ).select_related('booking', 'booking__client').order_by('-paid_at')
    else:
        payments = []

    return render(request, 'app/payment_dash.html', {'payments': payments})



@login_required
def availability_slot(request):
    user = request.user
    
    # Safety check: Only consultants should be here
    if user.role != 'CONSULTANT':
        messages.error(request, "Access denied. Only consultants can manage slots.")
        return redirect('home')

    profile, created = Consultant_Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Let use the Form to handle multiple date inputs
        formset = AvailabilityFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Availability slots updated!")
            return redirect('availability-slot')
    else:
        
        formset = AvailabilityFormSet(instance=profile)

    return render(request, 'app/availability_slot.html', {
        'formset': formset,
        'profile': profile
    })



@login_required
def session_review(request, booking_id):
    # Let fetch the actual booking/session being reviewed
    booking = get_object_or_404(Booking, id=booking_id)

    if hasattr(booking, 'review'): 
        messages.info(request, "You have already reviewed this session.")
        return redirect('book-dashboard')
    
    # Let prevent people who didn't book the session from reviewing it
    if booking.client != request.user:
        messages.error(request, "You can only review sessions you participated in.")
        return redirect('book-dashboard')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user
            review.booking = booking  
            
            review.consultant = booking.availability.consultant 
            
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect("book-dashboard")
    else:
        form = ReviewForm()

    return render(request, "app/session_review.html", {
        "form": form, 
        "booking": booking
    })


@login_required
def update_profile(request):
    if request.user.is_consultant: 
        form_class = ConsultantProfilePicForm
    else:
        form_class = ClientProfilePicForm

    if request.method == 'POST':
        
        form = form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated")
            return redirect('profile')
    else:
        form = form_class(instance=request.user)
    
    return render(request, 'app/update_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
             
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'app/change_password.html', {'form': form})


def forgot_password_step1(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
         
        user = CustomUser.objects.filter(username=identifier).first() or \
               CustomUser.objects.filter(email=identifier).first()
        
        if user:
            if user.security_question and user.security_answer:
                return redirect('forgot_password_step2', user_id=user.id)
            else:
                messages.error(request, "This account has no security question set. Please contact admin.")
        else:
            messages.error(request, "No account found with that username/email.")
            
    return render(request, 'app/forgot_password_step1.html')

def forgot_password_step2(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        answer = request.POST.get('answer')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Let use the method we wrote in your CustomUser model
        if user.check_security_answer(answer):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Success! Your password has been reset.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
        else:
            messages.error(request, "Incorrect answer to security question.")
            
    return render(request, 'app/forgot_password_step2.html', {'user': user})