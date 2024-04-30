from django.shortcuts import redirect
from functools import wraps

def check_registration_and_verification(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Check if the user has completed registration and OTP verification
            if not request.user.is_registered or not request.user.is_verified:
                # Redirect the user to the registration or OTP verification page
                return redirect('register')  # or 'verifyotp' depending on your setup
        return view_func(request, *args, **kwargs)
    return wrapper
