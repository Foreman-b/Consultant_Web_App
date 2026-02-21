from rest_framework import serializers
from .models import Availability, Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "availability", "reason_for_session", "consultant", 'created_at', 'status', 'consultant']
        read_only_fields = ("cleint", "status", "created_at",)


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ["id", "max_slot", "date", ]
        read_only_fields = ("consultant", "created_at",)