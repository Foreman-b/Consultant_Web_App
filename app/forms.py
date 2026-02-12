from django import forms
from .models import User, Consultant_Profile, Availability, Booking, Payment, Review

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'role']

class ConsultantProfileForm(forms.ModelForm):

    class Meta:
        model = Consultant_Profile
        fields = ['specialization', 'bio', 'meeting_platform', 'meeting_link', 'is_active']

class AvailabilityForm(forms.ModelForm):

    class Meta:
        model = Availability
        fields = ['date', 'max_slot']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['reason_for_session']

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ['amount']

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
