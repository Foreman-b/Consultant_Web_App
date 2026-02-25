from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Consultant_Profile, Availability, Booking, Payment, Review
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory



class UserRegisterForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    def clean_email(self):
        """
        Check if the email is already in use in the database.
        """
        email = self.cleaned_data.get('email')
        
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    

class ConsultantProfileForm(forms.ModelForm):

    class Meta:
        model = Consultant_Profile
        fields = ('specialization', 'bio', 'is_active')


class AvailabilityForm(forms.ModelForm):

    class Meta:
        model = Availability
        fields = ('date', 'max_slot',)
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

# This creates a group of forms for the Availability model
AvailabilityFormSet = forms.inlineformset_factory(
    Consultant_Profile, 
    Availability, 
    form=AvailabilityForm, 
    extra=1,      
    can_delete=True # Allows consultants to remove a date
)

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
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 
                'max': 5,
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Rate 1 to 5'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 4,
                'placeholder': 'Tell us about your session...'
            }),
        }



class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }