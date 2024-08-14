import logging
import os

from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
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
from .models import User, UserProfile, Post, PostForm
from .utils import load_unsplash_photo, set_top_message, get_user_photo_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    pass


class MyTokenRefreshView(TokenRefreshView):
    pass


def is_admin(user):
    return user.role == 'admin'


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
            user.role = 'user'  # Assign the 'user' role
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
        if profile.user != request.user and request.user.role != 'admin':
            return redirect('profile', user_id=request.user.id)
        form = UserProfileForm(instance=profile, user=request.user)
        top_message = request.session.get('top_message')
        if top_message:
            del request.session['top_message']

        user_photo_url = get_user_photo_url(profile)

        context = {
            'profile': profile,
            'form': form,
            'top_message': top_message,
            'user_photo_url': user_photo_url,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(View):
    template_name = 'user/profile.html'

    def post(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        if profile.user != request.user and not request.user.role == 'admin':
            return redirect('profile', user_id=request.user.id)
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            old_avatar_path = None
            if profile.user_photo:
                old_avatar_path = os.path.normpath(
                    os.path.join(settings.MEDIA_ROOT, 'avatars', os.path.basename(profile.user_photo.name)))
                logger.info(f"OLD AVATAR PATH FROM DATABASE: {old_avatar_path}")

            # Save the form to update the profile with the new avatar
            profile = form.save(commit=False)
            if 'user_photo' in request.FILES:
                new_avatar_path = os.path.normpath(
                    os.path.join(settings.MEDIA_ROOT, 'avatars', os.path.basename(request.FILES['user_photo'].name)))
                logger.info(f"NEW AVATAR PATH FROM FORM: {new_avatar_path}")
                logger.info(f"New avatar uploaded for user {profile.user.username}")
                profile.user_photo = request.FILES['user_photo']
            profile.save()

            # Delete the old avatar after the new one is saved
            if old_avatar_path:
                logger.info(f"Old avatar found for user {profile.user.username}, attempting to delete")
                try:
                    os.remove(old_avatar_path)
                    logger.info(f"Old avatar deleted for user {profile.user.username}")
                except Exception as e:
                    logger.error(f"Error deleting old avatar for user {profile.user.username}: {e}")
                # Check if the old avatar file still exists
                if os.path.exists(old_avatar_path):
                    logger.warning(
                        f"Old avatar file still exists for user {profile.user.username} at {old_avatar_path}")
                    logger.info(f"{old_avatar_path}")
                else:
                    logger.info(f"Old avatar file successfully deleted for user {profile.user.username}")
                    logger.info(f"{old_avatar_path}")

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
        if profile.user != request.user and not request.user.role == 'admin':
            return redirect('profile', user_id=request.user.id)
        return render(request, self.template_name, {'profile': profile})

    def post(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        if profile.user != request.user and not request.user.role == 'admin':
            return redirect('profile', user_id=request.user.id)
        user = profile.user
        if profile.user_photo:
            logger.info(f"Attempting to delete avatar for user {user.username}")
            try:
                old_avatar_path = os.path.normpath(
                    os.path.join(settings.MEDIA_ROOT, 'avatars', os.path.basename(profile.user_photo.name)))
                logger.info(f"OLD AVATAR PATH FROM DATABASE: {old_avatar_path}")
                os.remove(old_avatar_path)
                logger.info(f"Avatar deleted for user {user.username}")
            except Exception as e:
                logger.error(f"Error deleting avatar for user {user.username}: {e}")
            # Check if the avatar file still exists
            if os.path.exists(old_avatar_path):
                logger.warning(f"Avatar file still exists for user {user.username} at {old_avatar_path}")
                logger.info(f"{old_avatar_path}")
            else:
                logger.info(f"Avatar file successfully deleted for user {user.username}")
                logger.info(f"{old_avatar_path}")
        user.delete()
        set_top_message(request,
                        message_class=icons.WARNING_CLASS,
                        message_icon=icons.USER_DELETE_ICON,
                        message_text=f"{user.username} has been deleted!")
        if request.user.role == 'admin':
            return redirect('admin_user_list')
        logout(request)
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
        return render(request, self.template_name, {'posts': posts, 'username': request.user.username})


class PostEditView(View):
    template_name = 'user/edit_post.html'

    @method_decorator(login_required)
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.user != request.user and not request.user.role == 'admin':
            return redirect('my_posts')
        form = PostForm(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    @method_decorator(login_required)
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.user != request.user and not request.user.role == 'admin':
            return redirect('my_posts')
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            set_top_message(request,
                            message_class=icons.OK_CLASS,
                            message_icon=icons.OK_ICON,
                            message_text="Post updated successfully!")
            if request.user.role == 'admin':
                return redirect('admin_user_posts', user_id=post.user.id)
            return redirect('my_posts')
        return render(request, self.template_name, {'form': form, 'post': post})


class PostDeleteView(View):
    @method_decorator(login_required)
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user_id = post.user.id
        post.delete()
        set_top_message(request,
                        message_class=icons.WARNING_CLASS,
                        message_icon=icons.WARNING_ICON,
                        message_text="Post deleted successfully!")
        if request.user.role == 'admin':
            return redirect('admin_user_posts', user_id=user_id)
        return redirect('my_posts')


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminUserListView(View):
    template_name = 'admin/user_list.html'

    def get(self, request):
        users = User.objects.all()
        return render(request, self.template_name, {'users': users})


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminUserProfileView(View):
    template_name = 'user/profile.html'

    def get(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        form = UserProfileForm(instance=profile, user=request.user)
        user_photo_url = get_user_photo_url(profile)
        return render(request, self.template_name, {'form': form, 'profile': profile, 'user_photo_url': user_photo_url})


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminUserProfileEditView(View):
    template_name = 'user/profile.html'

    def post(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            old_avatar_path = None
            if profile.user_photo:
                old_avatar_path = os.path.normpath(
                    os.path.join(settings.MEDIA_ROOT, 'avatars', os.path.basename(profile.user_photo.name)))
                logger.info(f"OLD AVATAR PATH FROM DATABASE: {old_avatar_path}")

            # Save the form to update the profile with the new avatar
            profile = form.save(commit=False)
            if 'user_photo' in request.FILES:
                new_avatar_path = os.path.normpath(
                    os.path.join(settings.MEDIA_ROOT, 'avatars', os.path.basename(request.FILES['user_photo'].name)))
                logger.info(f"NEW AVATAR PATH FROM FORM: {new_avatar_path}")
                logger.info(f"New avatar uploaded for user {profile.user.username}")
                profile.user_photo = request.FILES['user_photo']
            profile.save()

            # Delete the old avatar after the new one is saved
            if old_avatar_path:
                logger.info(f"Old avatar found for user {profile.user.username}, attempting to delete")
                try:
                    os.remove(old_avatar_path)
                    logger.info(f"Old avatar deleted for user {profile.user.username}")
                except Exception as e:
                    logger.error(f"Error deleting old avatar for user {profile.user.username}: {e}")
                # Check if the old avatar file still exists
                if os.path.exists(old_avatar_path):
                    logger.warning(
                        f"Old avatar file still exists for user {profile.user.username} at {old_avatar_path}")
                    logger.info(f"{old_avatar_path}")
                else:
                    logger.info(f"Old avatar file successfully deleted for user {profile.user.username}")
                    logger.info(f"{old_avatar_path}")

            if 'role' in form.cleaned_data:
                logger.info(f"Role before change: {profile.user.role}")
                profile.user.role = form.cleaned_data['role']
                profile.user.save()
                logger.info(f"Role after change: {profile.user.role}")

            return redirect('profile', user_id=user_id)
        else:
            logger.error(form.errors)
        return render(request, self.template_name, {'form': form, 'profile': profile})


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminUserPostsView(View):
    template_name = 'user/my_posts.html'

    def get(self, request, user_id):
        posts = Post.objects.filter(user_id=user_id).order_by('-created_at')
        username = User.objects.get(id=user_id).username
        return render(request, self.template_name, {'posts': posts, 'username': username})


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminPostEditView(View):
    template_name = 'user/edit_post.html'

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        form = PostForm(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('admin_user_posts', user_id=post.user.id)
        return render(request, self.template_name, {'form': form, 'post': post})


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminDeleteProfileView(View):
    template_name = 'admin/confirm_delete.html'

    def get(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        return render(request, self.template_name, {'profile': profile})

    def post(self, request, user_id):
        profile = get_object_or_404(UserProfile, user_id=user_id)
        user = profile.user
        if profile.user_photo:
            logger.info(f"Attempting to delete avatar for user {user.username}")
            try:
                old_avatar_path = os.path.normpath(
                    os.path.join(settings.MEDIA_ROOT, 'avatars', os.path.basename(profile.user_photo.name)))
                logger.info(f"OLD AVATAR PATH FROM DATABASE: {old_avatar_path}")
                os.remove(old_avatar_path)
                logger.info(f"Avatar deleted for user {user.username}")
            except Exception as e:
                logger.error(f"Error deleting avatar for user {user.username}: {e}")
            # Check if the avatar file still exists
            if os.path.exists(old_avatar_path):
                logger.warning(f"Avatar file still exists for user {user.username} at {old_avatar_path}")
                logger.info(f"{old_avatar_path}")
            else:
                logger.info(f"Avatar file successfully deleted for user {user.username}")
                logger.info(f"{old_avatar_path}")
        user.delete()
        set_top_message(request,
                        message_class=icons.WARNING_CLASS,
                        message_icon=icons.USER_DELETE_ICON,
                        message_text=f"{user.username} has been deleted!")
        return redirect('admin_user_list')
