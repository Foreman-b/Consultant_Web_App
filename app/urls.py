from django.urls import path
from . import views
from django.conf import settings
from django.urls import re_path
from django.views.static import serve


urlpatterns = [
    path('', views.home,  name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book-dashboard/', views.book_dashboard, name='book-dashboard'),
    path('book-session/<int:availability_id>/', views.book_session, name='book-session'),
    path('update-status/<int:booking_id>/', views.update_booking_status, name='update-status'),

    path('consultant-dash', views.consultant_dash, name='consultant-dash'),
    path('availability-slot/', views.availability_slot, name='availability-slot'),
    path('update-link/<int:booking_id>/', views.update_meeting_link, name='update-link'),

    # Now let add payment urls
    path('pay/<int:booking_id>/', views.initialize_payment, name='initialize-payment'),
    path('verify-payment/', views.verify_payment, name='verify-payment'),
    path('payment-dash/', views.payment_dash, name='payment-dash'),


    # Let path for client profile
    path('profile/', views.user_profile, name='profile'),
    path('update-profile/', views.update_profile, name='update-profile'),
    

    # Let create session review right here
    path('review-session/<int:booking_id>/', views.session_review, name='session-review'),

    # Password reset and Forget Password
    path('profile/password/', views.change_password, name='change-password'),

    path('forgot-password/', views.forgot_password_step1, name='forgot_password_step1'),
    path('forgot-password/reset/<int:user_id>/', views.forgot_password_step2, name='forgot_password_step2'),
    

] 


urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]