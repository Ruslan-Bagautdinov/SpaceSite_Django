import base64
import os

from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from loguru import logger
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from templates import icons
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile, Post, PostForm
from .utils import load_unsplash_photo, set_top_message


class MyTokenObtainPairView(TokenObtainPairView):
    pass


class MyTokenRefreshView(TokenRefreshView):
    pass


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
        posts = Post.objects.all().order_by('-created_at')

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, 12)  # Show 12 posts per page

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = {
            "user": request.user if request.user.is_authenticated else None,
            "top_message": top_message,
            "unsplash_photo": unsplash_photo,
            "posts": posts
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
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response = HttpResponseRedirect(reverse('root'))
            response.set_cookie('access_token', access_token, httponly=True)
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
        logger.info(f'top_message at ProfileView get: {top_message}')
        if top_message:
            request.session.pop('top_message', None)

        user_photo_base64 = None
        if profile.user_photo:
            logger.info(f'User photo path: {profile.user_photo.path}')
            photo_path = profile.user_photo.path
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as photo_file:
                    user_photo_base64 = base64.b64encode(photo_file.read()).decode('utf-8')
            else:
                logger.info(f'Photo path does not exist: {photo_path}')
        else:
            logger.info('User photo is None')

        if not user_photo_base64:
            default_avatar_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'default_avatar.jpg')
            logger.info(f'Using default avatar path: {default_avatar_path}')
            with open(default_avatar_path, "rb") as default_photo_file:
                user_photo_base64 = base64.b64encode(default_photo_file.read()).decode('utf-8')

        logger.info(f'top_message before Profile render: {top_message}')
        context = {
            'profile': profile,
            'form': form,
            'top_message': top_message,
            'user_photo_base64': user_photo_base64
        }
        logger.info(f'context before Profile render: {context.get("top_message")}')
        return render(request, self.template_name, context)


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
        return render(request, self.template_name, {'profile': profile})

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


@method_decorator(login_required, name='dispatch')
class CreatePostView(View):
    template_name = 'user/create_post.html'

    def get(self, request):
        form = PostForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            set_top_message(request,
                            message_class=icons.OK_CLASS,
                            message_icon=icons.OK_ICON,
                            message_text="Post created successfully!")
            return redirect('root')
        return render(request, self.template_name, {'form': form})


class PostListView(View):
    template_name = 'user/my_posts.html'

    @method_decorator(login_required)
    def get(self, request):
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        return render(request, self.template_name, {'posts': posts})


class PostEditView(View):
    template_name = 'user/edit_post.html'

    @method_decorator(login_required)
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        form = PostForm(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    @method_decorator(login_required)
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            set_top_message(request,
                            message_class=icons.OK_CLASS,
                            message_icon=icons.OK_ICON,
                            message_text="Post updated successfully!")
            return redirect('my_posts')
        return render(request, self.template_name, {'form': form, 'post': post})


class PostDeleteView(View):
    @method_decorator(login_required)
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        set_top_message(request,
                        message_class=icons.WARNING_CLASS,
                        message_icon=icons.WARNING_ICON,
                        message_text="Post deleted successfully!")
        return redirect('my_posts')
