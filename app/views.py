from django.shortcuts import render, redirect


def home(request):
    return render(request, "app/home.html")