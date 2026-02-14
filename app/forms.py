from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Consultant_Profile, Availability, Booking, Payment, Review
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number',)

    def clean_email(self):
        """
        Check if the email is already in use in the database.
        """
        email = self.cleaned_data.get('email')
        # Check if any user already has this email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
class ConsultantProfileForm(forms.ModelForm):

    class Meta:
        model = Consultant_Profile
        fields = ('specialization', 'bio', 'is_active',)

class AvailabilityForm(forms.ModelForm):

    class Meta:
        model = Availability
        fields = ('date', 'max_slot',)
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ('reason_for_session',)

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ('amount',)

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ('rating', 'comment',)
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
