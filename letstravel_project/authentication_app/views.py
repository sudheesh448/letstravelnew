from imaplib import _Authenticator
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login,logout
from admin_side.models import PhoneNumber
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.utils import timezone
from twilio.rest import Client
from django.conf import settings

def register(request):
    if request.user.is_authenticated :
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            referral_code = request.POST.get('refferal_code')
            mobilenumber = request.POST.get('mobilenumber')

            
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
        
            if not PhoneNumber.objects.filter(referral_code=referral_code).exists():
                messages.error(request, "Invalid referral code..!!")
                return redirect('register')
        
            otp = get_random_string(length=6, allowed_chars='1234567890')
            expiry = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
            
            # Save the OTP and its expiry time in the session
            request.session['otp'] = otp
            request.session['otp_expiry'] = expiry.strftime('%Y-%m-%d %H:%M:%S')
            request.session['username'] = username  
            request.session['password'] = password1
            request.session['email'] = email
            request.session['Referral'] = referral_code
            request.session['mobilenumber'] = mobilenumber
            
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
        
        # context = {
        #     'username': request.session.get('username', ''),
        #     'email': request.session.get('email', ''),
        #     'password': request.session.get('password', ''),
        #     'referral_code': request.session.get('Referral', ''),
        #     'mobilenumber': request.session.get('mobilenumber', ''),
        # }

        return render(request, 'signup.html')


def verify_otp(request):
    if request.user.is_authenticated :
        return redirect('home')
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        saved_otp = request.session.get('otp')
        expiry = request.session.get('otp_expiry')

        if not saved_otp or not expiry:
            messages.error(request, 'somethging went wrong try again.')
            return redirect('register')

        if entered_otp == saved_otp and datetime.now() <= datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S'):
            # Valid OTP, register the user
            username = request.session.get('username')
            password = request.session.get('password')
            email = request.session.get('email')
            user =User.objects.create_user(username=username, password=password,email=email)


            referral_code=request.session['Referral'] 
            mobilenumber=request.session['mobilenumber'] 

            # Check if the referral code is valid and if it exists in the PhoneNumber table
            if referral_code and PhoneNumber.objects.filter(referral_code=referral_code).exists():
                referred_by = PhoneNumber.objects.get(referral_code=referral_code).user
                phone_number_instance = PhoneNumber.objects.get(user=user)
                phone_number_instance.phone_number = mobilenumber
                phone_number_instance.referred_by = referred_by
                phone_number_instance.save()

            messages.success(request, 'Registration successful!')
            del request.session['username']
            del request.session['password']
            del request.session['email']
            del request.session['Referral']
            del request.session['otp_expiry']
            del request.session['otp']
            return redirect('signin')
        
        elif datetime.now() > datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S'):
            messages.error(request, 'OTP expired try again.')
            return redirect('register')
        elif entered_otp != saved_otp:
            messages.error(request, 'Invalid OTP  try again.')
            return redirect('verify_otp')
    return render(request, 'verify.html')


def resend_otp(request):
    if request.user.is_authenticated :
        return redirect('home')
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
    return redirect('verify_otp')
    
    return render(request, 'verify.html')


# Function to generate a random OTP

# Function to send OTP to the user's email


def signin(request):
    if request.user.is_authenticated :
        return redirect('home')
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
    if request.user.is_authenticated :
        return redirect('home')
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_login')
        saved_otp = request.session.get('otp')
        expiry = request.session.get('otp_expiry')
        
        pk = request.session.get('pk')

        if not saved_otp or not expiry:
            messages.error(request, 'Something went wrong. please try agian.')
            return redirect('signin')

        if entered_otp == saved_otp and datetime.now() <= datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S'):
            # OTP verification successful
            user = User.objects.get(pk=pk)
            login(request, user)
            del request.session['email']
            del request.session['pk']
            del request.session['otp_expiry']
            del request.session['otp']
            return redirect('home')

        elif datetime.now() > datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S'):
            messages.error(request, 'OTP expired try again.')
            return redirect('signin')
        elif entered_otp != saved_otp:
            messages.error(request, 'Invalid OTP  try again.')
            return redirect('otp_verification')

    return render(request, 'verifylogin.html')


def resend_otp_signin(request):
        if request.user.is_authenticated :
             return redirect('home')    
        else:
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
    return redirect('home')


def signin_mobile_otp(request):
    if request.user.is_authenticated :
             return redirect('home')    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username,password=password)   
        if user is not None:
    # Generate a random OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')
            
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
        

        if not saved_otp or not expiry:    
            messages.error(request, 'OTP expired or invalid. Please try again.')
            return redirect('signin')
        
        if   saved_otp == entered_otp:
            # OTP verification successful
            user = User.objects.get(pk=pk)
            login(request, user)
            del request.session['otp']
            del request.session['otp_expiry']
            del request.session['pk']
            return redirect('home')
        messages.error(request, 'OTP expired or invalid. Please try again.')
        return redirect('mobile_otp_verification')
    return render(request, 'authentication/Mobileotpverify.html')

def forgotpassword(request):
    if request.user.is_authenticated :
             return redirect('home')
    if request.method == 'POST':
        # Get the user's email from the form
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Email not found in our records.')
            return redirect('forgot_password')

        # Generate a 6-digit OTP and save it in the user's session along with its expiry time
        otp = get_random_string(length=6, allowed_chars='1234567890')
        request.session['otp'] = otp
        request.session['otp_expiry'] = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        request.session['username'] = username
        request.session['pk'] = user.pk

        # Send the OTP to the user's email
        send_mail(
            'OTP Verification',
            f'Your OTP for reseting password is: {otp}',
            'letstravelllp@gmail.com',
            [user.email],
            fail_silently=False,
        )
        messages.success(request, 'OTP sent to your email ID!')
        return redirect('enter_otp_forgot_password')  # Redirect to the page where the user enters OTP

    return render(request, 'authentication/forgotpassword.html')

def enter_otp_forgot_password(request):
    if request.user.is_authenticated :
             return redirect('home')    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        username = request.session.get('username')
        otp_expiry_str = request.session.get('otp_expiry')

        if username and otp_expiry_str:
            otp_expiry = datetime.strptime(otp_expiry_str, '%Y-%m-%d %H:%M:%S')
            otp_expiry = otp_expiry.replace(tzinfo=None)  # Convert to offset-naive datetime
            current_time = timezone.now().replace(tzinfo=None)

            if current_time <= otp_expiry:
                saved_otp = request.session.get('otp')

                if entered_otp == saved_otp:
                    return redirect('reset_password')  # Redirect to the password reset form
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
            else:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
        else:
            messages.error(request, 'OTP verification failed. Please request a new OTP.')

    return render(request, 'authentication/otp_forgotpassword.html')

def reset_password(request):
    if request.user.is_authenticated :
             return redirect('home')    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        username = request.session.get('username')

        if password1 != password2:
                messages.error(request,"Passwords didn't match !")
                return redirect('reset_password')

        if username:
            try:
                user = User.objects.get(username=username)
                user.set_password(password1)
                user.save()
                messages.success(request, 'Password reset successful. You can now log in with your new password.')
                return redirect('signin')  # Redirect to the login page after successful password reset
            except User.DoesNotExist:
                messages.error(request, 'User not found. Please request a new OTP.')
        else:
            messages.error(request, 'Password reset failed. Please request a new OTP.')

    return render(request, 'authentication/resetpassword.html')
