# Create your models here.

from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models


from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=128)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES, default='user')

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


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]  # Return the first 50 characters of the post content

    def truncated_content(self):
        return self.content[:300] + '...' if len(self.content) > 500 else self.content


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
