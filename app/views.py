from django.shortcuts import render, redirect
from .models import Availability, Booking
from .forms import (
    UserRegisterForm, ConsultantProfileForm,
    AvailabilityForm, BookingForm, PaymentForm, ReviewForm,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404



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
