from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_secret = models.CharField(max_length=16)  # Adjust max_length as needed
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
