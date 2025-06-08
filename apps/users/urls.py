# apps/users/urls.py

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),

    # Authentication URLs
    path('auth/', views.PhoneAuthView.as_view(), name='phone_auth'),
    path('verify/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('resend/', views.ResendCodeView.as_view(), name='resend_code'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Profile URLs
    path('complete-profile/', views.CompleteProfileView.as_view(), name='complete_profile'),
]
