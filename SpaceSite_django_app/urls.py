from django.urls import path

from .views import (
    RootView, LoginView, LogoutView, RegisterView, ProfileView, ProfileUpdateView, DeleteProfileView,
    CreatePostView, PostListView, PostEditView, PostDeleteView, AdminUserListView, AdminUserProfileView,
    AdminUserPostsView, AdminPostEditView, AdminDeleteProfileView, AdminUserProfileEditView
)

urlpatterns = [
    path('', RootView.as_view(), name='root'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('profile/<int:user_id>/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/<int:user_id>/delete/', DeleteProfileView.as_view(), name='delete_profile'),
    path('create-post/', CreatePostView.as_view(), name='create_post'),
    path('my-posts/', PostListView.as_view(), name='my_posts'),
    path('edit-post/<int:post_id>/', PostEditView.as_view(), name='edit_post'),
    path('delete-post/<int:post_id>/', PostDeleteView.as_view(), name='delete_post'),
    path('for-admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('for-admin/user/<int:user_id>/profile/', AdminUserProfileView.as_view(), name='admin_user_profile'),
    path('for-admin/user/<int:user_id>/profile/edit/', AdminUserProfileEditView.as_view(), name='admin_user_profile_edit'),
    path('for-admin/user/<int:user_id>/posts/', AdminUserPostsView.as_view(), name='admin_user_posts'),
    path('for-admin/edit-post/<int:post_id>/', AdminPostEditView.as_view(), name='admin_edit_post'),
    path('for-admin/user/<int:user_id>/delete/', AdminDeleteProfileView.as_view(), name='admin_delete_profile'),
]