# forms.py
from django import forms

from .models import User, UserProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class UserProfileForm(forms.ModelForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'user_photo', 'user_age']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if user is not None and user.role != 'admin':
            del self.fields['role']
        elif user is None:
            del self.fields['role']
