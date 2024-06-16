from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from .views import RootView

urlpatterns = [
    path('', RootView.as_view(), name='root'),
    path('login/', LoginView.as_view(template_name='user/login.html'), name='login'),
    path('register/', views.register, name='register'),

    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.MyTokenRefreshView.as_view(), name='token_refresh'),

]
