from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid


# Let create model that handle users both client and consultant details
class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        # Role for both client and consultant
        CLIENT = "CLIENT", "Client"
        CONSULTANT = "CONSULTANT", "consultant"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="upload/profile_picture", null=True, blank=True)

    SECURITY_QUESTIONS = [
        ('pet', "What was the name of your first pet?"),
        ('city', "In what city were you born?"),
        ('school', "What was the name of your elementary school?"),
    ]
    security_question = models.CharField(max_length=255, choices=SECURITY_QUESTIONS, blank=True, null=True)
    security_answer = models.CharField(max_length=255, blank=True, null=True)
    
    def check_security_answer(self, raw_answer):
        # We lowercase and strip to avoid "Cat" vs "cat" issues
        return self.security_answer.lower().strip() == raw_answer.lower().strip()
    
    def save(self, *args, **kwargs):
        if self.security_answer:
            self.security_answer = self.security_answer.lower().strip()
        super().save(*args, **kwargs)

    @property
    def is_consultant(self):
        return self.role == self.Role.CONSULTANT

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT


class Consultant_Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} ({self.specialization})"
        return f"Profile ID {self.id} (No User Linked)"
    

class Availability(models.Model):
    consultant = models.ForeignKey(Consultant_Profile, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    max_slot = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('consultant', 'date')

    def is_full(self):
        # Let count how many confirmed bookings exist for this specific availability record
        return self.bookings.filter(status='CONFIRMED').count() >= self.max_slot

    def __str__(self):
        return f"{self.consultant.user.username} - {self.date} ({self.max_slot} max)"



class Booking(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='client_bookings'
        )
    consultant = models.ForeignKey(
        Consultant_Profile, 
        on_delete=models.CASCADE,
        related_name='consultant_bookings'
        )
    availability = models.ForeignKey(
        Availability, 
        on_delete=models.CASCADE,
        related_name='bookings'
        )
    reason_for_session = models.TextField()
    meeting_platform = models.CharField(max_length=50, blank=True, null=True)
    meeting_link = models.URLField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING           
    )
    created_at = models.DateTimeField(auto_now_add=True)

   

    def __str__(self):
        client_name = self.client.username if self.client else "No Client"
        
        consultant_name = self.consultant.user.username if self.consultant and self.consultant.user else "No Consultant"
        
        date = self.availability.date if self.availability else "No Date"
        
        return f"Booking: {client_name} -> {consultant_name} ({date})"

    @property
    def is_paid(self):
        if hasattr(self, 'payment'): 
            return self.payment.status == 'SUCCESS'
        return False


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
    
    booking = models.OneToOneField(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='payment'
    )
    amount = models.PositiveIntegerField()
    # Let handle the payment reference 
    payment_reference = models.CharField(
        max_length=100, 
        unique=True, 
        null=True,
        default=uuid.uuid4,     # This generate reference automatically
        editable=False
        )
    status =  models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment: {self.amount} - {self.status} (Ref {self.payment_reference})"
    
    @property
    def amount_in_naira(self):
        return self.amount / 100


class Review(models.Model):
    # Link to the specific booking
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='review')
    # Link to the person writing it
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    # Link to the consultant (derived from booking)
    consultant = models.ForeignKey('Consultant_Profile', on_delete=models.CASCADE, null=True, blank=True)
    
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Review ({self.rating} stars) for {self.booking.consultant.user.username}"