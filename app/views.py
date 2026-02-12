from django.shortcuts import render, redirect
from .forms import (
    UserRegisterForm, ConsultantProfileForm,
    AvailabilityForm, BookingForm, PaymentForm, ReviewForm,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


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