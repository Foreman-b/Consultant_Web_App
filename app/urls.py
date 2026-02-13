from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home,  name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book-dashboard/', views.book_dashboard, name='book-dashboard'),
    path('book-session/<int:availability_id>/', views.book_session, name='book-session'),

]