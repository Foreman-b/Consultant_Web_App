from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home,  name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book-dashboard/', views.book_dashboard, name='book-dashboard'),
    path('book-session/<int:availability_id>/', views.book_session, name='book-session'),
    path('consultant-dash', views.consultant_dash, name='consultant-dash'),
    path('update-status/<int:booking_id>/', views.update_booking_status, name='update-status'),
    path('update-link/<int:booking_id>/', views.update_meeting_link, name='update-link'),

    # Now let add payment urls
    path('pay/<int:booking_id>/', views.initialize_payment, name='initialize-payment'),
    path('verify-payment/', views.verify_payment, name='verify-payment'),
    path('payment-dash/', views.payment_dash, name='payment-dash'),


    # Let path for client profile
    path('profile/', views.user_profile, name='profile'),
    path('availability-slot/', views.availability_slot, name='availability-slot'),

    # Let create session review right here
    path('review-session/<int:booking_id>/', views.session_review, name='session-review'),


    

] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)