from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView, ForgotPasswordView, ResetPasswordView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh-token/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    path('me/', UserProfileView.as_view(), name='user-profile'),
    
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
