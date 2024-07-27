

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=128)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    user_photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    user_age = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.username
