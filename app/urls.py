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


    # Let path for client profile
    path("profile/", views.profile_settings, name="profile"),

] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)