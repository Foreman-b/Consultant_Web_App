from rest_framework.routers import DefaultRouter
from .viewsets import BookingViewSet, AvailabilityViewSet
from django.urls import path, include


# This is for consultant to update the availability
consultant_router = DefaultRouter()
consultant_router.register("availabilities", AvailabilityViewSet, basename="consultant-avail")

# Client specific routes, to perform CRUD for Bookings
client_router = DefaultRouter()
client_router.register("bookings", BookingViewSet, basename="client-bookings")


urlpatterns = [
    path('consultant/', include(consultant_router.urls)),
    path('client/', include(client_router.urls)),
]
