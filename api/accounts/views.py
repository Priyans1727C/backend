from rest_framework import generics
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer, UserProfileSerializer, UserProfileUpdateSerializer


from .models import UserProfile
from rest_framework.permissions import IsAuthenticated








class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_token = str(refresh)

        # Build response
        response = Response({
            'access': access,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
            }
        }, status=status.HTTP_201_CREATED)

        # Set the refresh token as HttpOnly cookie
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,        # Set to False if you're not using HTTPS in development
            samesite='None',    # Use 'Lax' for local dev without HTTPS
            path='/',
            max_age=3600,       # 1 hour; adjust as needed
        )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.get('refresh')
            if refresh_token:
                # For local development, use samesite 'Lax' with secure set to False.
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,        # Prevents JavaScript access
                    secure=True,          # Use False in development if not on HTTPS
                    samesite='None',        # 'Lax' works better with secure=False for local testing
                    path='/',
                    max_age=3600,          # Expiration time in seconds
                   
                    
                )
                # Optionally remove the refresh token from the response body.
                response.data.pop('refresh', None)
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # If the client hasn't supplied the refresh token in the request data,
        # attempt to get it from the cookies.
        if 'refresh' not in request.data:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                request.data['refresh'] = refresh_token
        
        return super().post(request, *args, **kwargs)
    
    
    
    
#Passwrod reset

class ForgotPasswordView(APIView):
    # No authentication required for password reset
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # Construct your reset URL (this should point to your frontend reset page)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
            # Send the email with the reset link
            send_mail(
                subject="Reset Your Password",
                message=f"Click the link below to reset your password:\n{reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        # Always respond with success to avoid email enumeration.
        return Response(
            {"detail": "If an account with that email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK,
        )

class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Debugging: Print user details after password reset
        # print(f"Password reset for: {user.email}, New password: {user.password}")

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Protect the view with JWT authentication

    def post(self, request):
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('refresh_token')  # Remove the refresh token cookie
        return response




class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Protect the view with JWT authentication

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({
                "id": request.user.id,
                "user": request.user.username,
                "message": "UserProfile not found. Returning basic user info."
            })

    def put(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileUpdateSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)