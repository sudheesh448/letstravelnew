from django.urls import path
from . import views



urlpatterns = [
    path('register', views.register, name='register'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('resend/', views.resend_otp, name='resend_otp'),
    path('signin/', views.signin, name='signin'),
    path('verifysign/', views.otp_verification, name='otp_verification'),
    path('resendotpsignin/', views.resend_otp_signin, name='resend_otp_signin'),
    path('signout/', views.signout, name='signout'),
    
]


