from imaplib import _Authenticator
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login,logout


def register(request):
    if request.user.is_authenticated :
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if User.objects.filter(username=username):
                messages.error(request, "Username already exist..!!")
                return redirect('register')
            
            if User.objects.filter(email=email):
                messages.error(request," Email already registered..!!")
                return redirect('register')
            
            if password1 != password2:
                messages.error(request,"Passwords didn't match !")
                return redirect('register')
            
            if not username.isalnum():
                messages.error(request,"Username must be Alpha-Numeric")
                return redirect('register')
            otp = get_random_string(length=6, allowed_chars='1234567890')
            expiry = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
            
            # Save the OTP and its expiry time in the session
            request.session['otp'] = otp
            request.session['otp_expiry'] = expiry.strftime('%Y-%m-%d %H:%M:%S')
            request.session['username'] = username  
            request.session['password'] = password1
            request.session['email'] = email
            
            # Send the OTP to the user's email
            send_mail(
                'OTP Verification',
                f'Your OTP is: {otp}',
                'your_email@example.com',  # Replace with your email address
                [email],
                fail_silently=False,
            )
            messages.success(request, 'OTP send to your email ID!')
            
            return redirect('verify_otp')
        
        return render(request, 'signup.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('otp')
        expiry = request.session.get('otp_expiry')

        if not saved_otp or not expiry:
            messages.error(request, 'OTP expired or invalid. Please try again.')
            return redirect('register')

        if entered_otp == saved_otp and datetime.now() <= datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S'):
            # Valid OTP, register the user
            username = request.session.get('username')
            password = request.session.get('password')
            email = request.session.get('email')
            User.objects.create_user(username=username, password=password,email=email)
            messages.success(request, 'Registration successful!')
            del request.session['username']
            del request.session['password']
            del request.session['email']
            return redirect('signin')
        messages.error(request, 'OTP expired or invalid. Please try again.')
        return redirect('register')
    return render(request, 'verify.html')


def resend_otp(request):
    email = request.session.get('email')
    print("eeee")
    otp = get_random_string(length=6, allowed_chars='1234567890')
    expiry = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        # Update the OTP and its expiry time in the session
    request.session['otp'] = otp
    request.session['otp_expiry'] = expiry.strftime('%Y-%m-%d %H:%M:%S')
        # Send the new OTP to the user's email
    send_mail(
        'OTP Verification',
        f'Your new OTP is: {otp}',
        'your_email@example.com',  # Replace with your email address
        [email],
        fail_silently=False,
    )
    messages.success(request, 'OTP send to your email ID!')
    print(send_mail)
        
    messages.info(request, 'New OTP sent. Please check your email.')
    return redirect('verify_otp')
    
    return render(request, 'verify.html')


# Function to generate a random OTP

# Function to send OTP to the user's email


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # User is authenticated with password

            # Generate OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')

            # Save OTP and its expiry time in session
            request.session['otp'] = otp
            request.session['otp_expiry'] = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
            email=user.email
            request.session['email'] = user.email
            request.session['pk'] = user.pk

            # Send OTP to user's email
            send_mail(
                'OTP Verification',
                f'Your OTP is: {otp}',
                'letstravelllp@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, 'OTP send to your email ID!')

            return redirect('otp_verification')
        else:
            # Invalid credentials
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')

def otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_login')
        saved_otp = request.session.get('otp')
        expiry = request.session.get('otp_expiry')
        
        pk = request.session.get('pk')

        if not saved_otp or not expiry:
            messages.error(request, 'OTP expired or invalid. Please try again.')
            return redirect('signin')

        if entered_otp == saved_otp and datetime.now() <= datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S'):
            # OTP verification successful
            user = User.objects.get(pk=pk)
            login(request, user)
            return redirect('home')

        messages.error(request, 'OTP expired or invalid. Please try again.')
        return redirect('otp_verification')

    return render(request, 'verifylogin.html')


def resend_otp_signin(request):    
        email = request.session.get('email')
        otp = get_random_string(length=6, allowed_chars='1234567890')
        expiry = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        # Update the OTP and its expiry time in the session
        request.session['otp'] = otp
        request.session['otp_expiry'] = expiry.strftime('%Y-%m-%d %H:%M:%S')
        # Send the new OTP to the user's email
        send_mail(
            'OTP Verification',
            f'Your new OTP is: {otp}',
            'your_email@example.com',  # Replace with your email address
            [email],
            fail_silently=False,
        )
        messages.success(request, 'OTP send to your email ID!')
        messages.info(request, 'New OTP sent. Please check your email.')
        return redirect('otp_verification')

def signout(request):
    if request.user.is_authenticated:
        logout(request)
    messages.success(request, "Logged Out Successfully")
    return redirect('home')


def signin_mobile_otp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username)

        user = authenticate(request, username=username,password=password)
        print(user)
        if user is not None:
    # Generate a random OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')
            print(otp)
    # Get the user's phone number from the request or any other source
            phone_number = '+918086611001'  # Replace with the user's actual phone number

    # Send the OTP via Twilio
            send_otp(phone_number, otp)
            messages.success(request, 'OTP send to your mobile no!')
            request.session['otp'] = otp
            request.session['otp_expiry'] = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
            request.session['pk'] = user.pk
            return redirect('mobile_otp_verification')
        

    # ... Continue with your logic or rendering the response
    return render(request, 'authentication/MobileOtpLogin.html')



from twilio.rest import Client
from django.conf import settings

def send_otp(phone_number, otp):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_phone_number = settings.TWILIO_PHONE_NUMBER

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=twilio_phone_number,
        to=phone_number
    )

    return None

def mobile_otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('mobile_otp_login')
        saved_otp = request.session.get('otp')
        expiry = request.session.get('otp_expiry')
        pk = request.session.get('pk')
        print(saved_otp)
        print(expiry)
        print(pk)
        print(entered_otp)

        if not saved_otp or not expiry:
            print("sf")
            messages.error(request, 'OTP expired or invalid. Please try again.')
            return redirect('signin')
        
        if  saved_otp:
            print("hii")

        if   saved_otp == entered_otp:
            # OTP verification successful
            print("s")
            messages.success(request, 'OTP verified successfully')
            user = User.objects.get(pk=pk)
            login(request, user)
            return redirect('home')

        messages.error(request, 'OTP expired or invalid. Please try again.')
        return redirect('mobile_otp_verification')

    return render(request, 'authentication/Mobileotpverify.html')


