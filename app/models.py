from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid


# Let create model that handle users both client and consultant details
class User(AbstractUser):

    class Role(models.TextChoices):
        # For our user let define each role for both client and consultant
        CLIENT = "CLIENT", "Client"
        CONSULTANT = "CONSULTANT", "consultant"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

# Now let create deatisl for consultant profile
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

    # def __str__(self):
    #     return f"{self.user.username} - {self.specialization}"
    # def __str__(self):
    #     if self.user:
    #         return f"{self.user.username} - {self.specialization}"
    #     return f"No User Assigned - {self.specialization}"
    def __str__(self):
        # Always check if self.user exists to avoid the AttributeError
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

    # def __str__(self):
    #     return f"Booking: {self.client.username} -> {self.consultant.username} ({self.availability.date})"
    # app/models.py

def __str__(self):
    # Use .user.username instead of .username for the consultant
    client_name = self.client.username if self.client else "No Client"
    
    # Hop through the 'user' relationship of the Consultant_Profile
    consultant_name = self.consultant.user.username if self.consultant and self.consultant.user else "No Consultant"
    
    date = self.availability.date if self.availability else "No Date"
    
    return f"Booking: {client_name} -> {consultant_name} ({date})"



class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Let handle the payment reference 
    payment_reference = models.CharField(
        max_length=100, 
        unique=True, null=True,
        default=uuid.uuid4,     # This generate reference automatically
        editable=False
        )
    status =  models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment: {self.amount} - {self.status} (Ref {self.payment_reference})"


class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Review ({self.rating} stars) for {self.booking.consultant.user.username}"