from django.urls import path
from . import views



urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('resend/', views.resend_otp, name='resend_otp'),
    path('signin/', views.signin, name='signin'),
    path('verifysign/', views.otp_verification, name='otp_verification'),
    path('resendotpsignin/', views.resend_otp_signin, name='resend_otp_signin'),
    path('signout/', views.signout, name='signout'),
    path('signin_mobile_otp/', views.signin_mobile_otp, name='signin_mobile_otp'),
    path('mobile_otp_verification/', views.mobile_otp_verification, name='mobile_otp_verification'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('enter_otp/', views.enter_otp_forgot_password, name='enter_otp_forgot_password'),
    path('reset_password/', views.reset_password, name='reset_password'),

]


