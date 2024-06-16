from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response


from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile
from .utils import load_unsplash_photo
from templates import icons


class MyTokenObtainPairView(TokenObtainPairView):
    pass


class MyTokenRefreshView(TokenRefreshView):
    pass

# Create your views here.


class RootView(View):
    def get(self, request):
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

        return render(request, 'root.html', context)







def register(request):
    if request.method == 'POST':
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
            response = redirect('root_view')
            response.set_cookie('access_token', access_token, httponly=True)
            return response
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'user/register.html', {'user_form': user_form, 'profile_form': profile_form})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'user/profile.html', {'profile': profile})
