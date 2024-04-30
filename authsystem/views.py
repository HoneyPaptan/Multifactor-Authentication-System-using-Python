from django.shortcuts import render, redirect
from django.contrib.auth.models import User
import pyotp
# Import the custom decorator
from .decorators import check_registration_and_verification
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
from .forms import RegistrationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
def send_otp(email, otp_secret):
    otp = pyotp.TOTP(otp_secret)
    otp_code = otp.now()

    send_mail(
        'OTP Verification',
        f'Your OTP is: {otp_code}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
def registerPage(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(email=email)
                if user.userprofile.is_verified:
                    # User is already registered and verified
                    messages.error(request, 'Email is already registered. Please log in.')
                    return redirect('login')
                
                # Update the OTP secret and resend OTP
                user_profile = user.userprofile
                user_profile.otp_secret = pyotp.random_base32()
                user_profile.save()
                send_otp(email, user_profile.otp_secret)
                messages.info(request, 'Invalid OTP. New OTP sent. Please check your email.')
                return redirect('verifyotp')

            except User.DoesNotExist:
                # Create a new user
                user = User.objects.create_user(username=username, email=email, password=password)

            # Generate OTP
            otp_secret = pyotp.random_base32()
            otp = pyotp.TOTP(otp_secret)
            otp_code = otp.now()

            # Create or update UserProfile instance
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.otp_secret = otp_secret
            user_profile.save()
            
            # Send OTP via email
            send_otp(email, otp_secret)
            
            # Redirect to OTP verification page
            return redirect('verifyotp', identifier=email)  # Pass email as identifier

    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def verify_otp(request, identifier):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        
        try:
            user_profile = UserProfile.objects.get(user__email=identifier)
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid email. Please register again.')
            return redirect('register')
        
        otp_secret = user_profile.otp_secret
        
        # Verify OTP
        otp = pyotp.TOTP(otp_secret)
        if otp.verify(otp_entered):
            # OTP verified, set user as verified
            user_profile.is_verified = True
            user_profile.save()
            
            # Log in user
            user = user_profile.user
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Manually set authentication backend
            login(request, user)
            messages.success(request, 'OTP verified. You are now logged in.')
            return redirect('home')
        else:
            # OTP verification failed, resend OTP
            otp = pyotp.TOTP(otp_secret)
            if otp.verify(otp_entered):
                # OTP verified, set user as verified
                user_profile.is_verified = True
                user_profile.save()
                
                # Log in user
                user = user_profile.user
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # Manually set authentication backend
                login(request, user)
                messages.success(request, 'OTP verified. You are now logged in.')
                return redirect('home')
            else:
                # Invalid OTP entered, send a new OTP
                send_otp(user_profile.user.email, user_profile.otp_secret)
                messages.error(request, 'Invalid OTP. New OTP sent. Please check your email.')
                return redirect('verifyotp', identifier=identifier)

    return render(request, 'verify.html')


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect("login")  # Display error message for invalid login attempt
    
    return render(request, 'login.html')

@login_required
def homePage(request):
    return render(request, "home.html")
@login_required
def logoutPage(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout