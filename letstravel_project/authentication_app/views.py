from imaplib import _Authenticator
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
        
        messages.info(request, 'New OTP sent. Please check your email.')
        return redirect('otp_verification')



def signout(request):
    if request.user.is_authenticated:
        logout(request)
    messages.success(request, "Logged Out Successfully")
    return redirect('home')