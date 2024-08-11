from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.RootView.as_view(), name='root'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/<int:user_id>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<int:user_id>/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/<int:user_id>/delete/', views.DeleteProfileView.as_view(), name='delete_profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-post/', views.CreatePostView.as_view(), name='create_post'),
    path('my-posts/', views.PostListView.as_view(), name='my_posts'),
    path('edit-post/<int:post_id>/', views.PostEditView.as_view(), name='edit_post'),
    path('delete-post/<int:post_id>/', views.PostDeleteView.as_view(), name='delete_post'),
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/user/<int:user_id>/profile/', views.AdminUserProfileView.as_view(), name='admin_user_profile'),
    path('admin/user/<int:user_id>/posts/', views.AdminUserPostsView.as_view(), name='admin_user_posts'),
    path('admin/post/<int:post_id>/edit/', views.AdminPostEditView.as_view(), name='admin_edit_post'),
]
