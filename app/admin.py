from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Consultant_Profile, Availability,
    Booking, Payment, Review
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'role'),
        }),
    )
# Let allow adding availability inside the Consultant profile
class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

@admin.register(Consultant_Profile)
class ConsultantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'is_active', 'created_at')
    search_fields = ('user__username', 'specialization')
    inlines = [AvailabilityInline]

# Let handle the booking session on admin dashboard
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'consultant', 'availability', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username', 'consultant__user__username')

# We need payment to be saved too
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'payment_reference', 'paid_at')
    list_filter = ('status',)

# Review is actually optional
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')
    readonly_fields = ('created_at',)


