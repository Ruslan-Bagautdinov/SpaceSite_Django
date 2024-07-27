
import base64
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken




from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile
from .utils import load_unsplash_photo, set_top_message, redirect_with_message
from templates import icons


class MyTokenObtainPairView(TokenObtainPairView):
    pass


class MyTokenRefreshView(TokenRefreshView):
    pass

# Create your views here.


class RootView(View):
    def get(self, request):

        template_name = 'root.html'

        top_message = request.session.get('top_message')

        if top_message is None:
            if request.user.is_authenticated:
                text = f"Hello, {request.user.username}!"
            else:
                text = "Welcome to our site!"
            top_message = {
                "class": "alert alert-light rounded",
                "icon": icons.HI_ICON,
                "text": text
            }
        else:
            del request.session['top_message']

        unsplash_photo = load_unsplash_photo('universe galaxy cosmos')
        if unsplash_photo is None:
            unsplash_photo = '/static/img/default_unsplash.jpg'

        context = {
            "user": request.user if request.user.is_authenticated else None,
            "top_message": top_message,
            "unsplash_photo": unsplash_photo
        }

        return render(request, template_name, context)


class LoginView(APIView):

    template_name = 'user/login.html'

    def get(self, request, *args, **kwargs):
        top_message = request.session.get('top_message')
        if top_message:
            request.session.pop('top_message', None)
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
        context = {
            "user": request.user if request.user.is_authenticated else None,
            "top_message": top_message,
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            set_top_message(request,
                            message_class=icons.OK_CLASS,
                            message_icon=icons.OK_ICON,
                            message_text=f"You are logged in with the account: {username}")
            return HttpResponseRedirect(reverse('root'))
        else:
            set_top_message(request,
                            message_class=icons.WARNING_CLASS,
                            message_icon=icons.WARNING_ICON,
                            message_text="Incorrect username or password")
            return HttpResponseRedirect(reverse('login'))


class LogoutView(APIView):

    def get(self, request):
        logout(request)
        set_top_message(request,
                        message_class=icons.INFO_CLASS,
                        message_icon=icons.WARNING_ICON,
                        message_text="You have been logged out successfully.")
        return HttpResponseRedirect(reverse('login'))


class RegisterView(View):
    template_name = 'user/register.html'

    def get(self, request, *args, **kwargs):
        top_message = request.session.get('top_message')
        if top_message:
            request.session.pop('top_message', None)
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
        context = {
            "user": request.user if request.user.is_authenticated else None,
            "top_message": top_message,
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)  # Hash the password
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Store the access token in a cookie
            response = HttpResponseRedirect(reverse('root'))
            response.set_cookie('access_token', access_token, httponly=True)

            # Set top message
            set_top_message(request,
                            message_class=icons.OK_CLASS,
                            message_icon=icons.OK_ICON,
                            message_text=f"You are logged in with the account: {user.username}")

            return response

        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'user/profile.html'

    def get(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        if profile.user != request.user:
            return redirect('profile', user_id=request.user.id)
        form = UserProfileForm(instance=profile)
        top_message = request.session.get('top_message')
        if top_message:
            del request.session['top_message']

        # Handle user photo
        user_photo_base64 = None
        if profile.user_photo:
            photo_path = profile.user_photo.path
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as photo_file:
                    user_photo_base64 = base64.b64encode(photo_file.read()).decode('utf-8')

        if not user_photo_base64:
            default_avatar_path = os.path.join(settings.STATIC_ROOT, 'img', 'default_avatar.jpg')
            with open(default_avatar_path, "rb") as default_photo_file:
                user_photo_base64 = base64.b64encode(default_photo_file.read()).decode('utf-8')

        context = {
            'profile': profile,
            'form': form,
            'top_message': top_message,
            'user_photo_base64': user_photo_base64
        }
        return render(request, self.template_name, context)

    def post(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        if profile.user != request.user:
            return redirect('profile', user_id=request.user.id)
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            set_top_message(request,
                            message_class=icons.OK_CLASS,
                            message_icon=icons.OK_ICON,
                            message_text=f"{request.user.username}, Your profile has been updated!")
            return redirect('profile', user_id=user_id)
        return render(request, self.template_name, {'form': form})

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(View):
    template_name = 'user/profile.html'

    def post(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        if profile.user != request.user:
            return redirect('profile', user_id=request.user.id)
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            set_top_message(request,
                            message_class=icons.OK_CLASS,
                            message_icon=icons.OK_ICON,
                            message_text=f"{request.user.username}, Your profile has been updated!")
            return redirect('profile', user_id=user_id)
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class DeleteProfileView(View):
    template_name = 'user/confirm_delete.html'

    def get(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        if profile.user != request.user:
            return redirect('profile', user_id=request.user.id)
        return render(request, self.template_name)

    def post(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        if profile.user != request.user:
            return redirect('profile', user_id=request.user.id)
        user = profile.user
        user.delete()
        logout(request)
        set_top_message(request,
                        message_class=icons.WARNING_CLASS,
                        message_icon=icons.USER_DELETE_ICON,
                        message_text=f"{user.username} has been deleted!")
        response = redirect('login')
        response.delete_cookie('access_token')
        return response
