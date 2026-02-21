from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .permissions import IsConsultant, IsClient
from .models import Booking, Availability
from .serializers import BookingSerializer, AvailabilitySerializer



class AvailabilityViewSet(ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    # ONLY Consultants can even see this endpoint exists/works
    permission_classes = [IsConsultant] 

    def get_queryset(self):
        return Availability.objects.filter(consultant__user=self.request.user)

    def perform_create(self, serializer):
    # Pass the profile instance, not the user instance
        serializer.save(consultant=self.request.user.profile)

class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    # Let allow only client to be able to use booking api
    permission_classes = [IsClient]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CONSULTANT':
            # Consultants see bookings made for their slots
            return Booking.objects.filter(availability__consultant__user=user)
        # Clients see bookings they created
        return Booking.objects.filter(client=user)

    def perform_create(self, serializer):
        # This line fixes the NOT NULL constraint error.
        # It tells Django: "Take the person logged in right now and set them as the client."
        serializer.save(client=self.request.user)