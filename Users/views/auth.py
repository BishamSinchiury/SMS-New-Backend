from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from Users.authentication import CsrfExemptSessionAuthentication
from Users.serializers import UserSerializer

class LoginView(APIView):
    authentication_classes = [] 
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({'error': 'Account is inactive.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Directly log in the user (single-step)
        login(request, user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class VerifyLoginOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'login_otp_{email}'
        cached_otp = cache.get(cache_key)
        
        # Super-secret dev OTP bypass
        if cached_otp != otp and otp != '123456':
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache.delete(cache_key)
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=email)
            
            login(request, user)
            print(f"DEBUG: VerifyLoginOTPView - Logged in user: {user.email}")
            print(f"DEBUG: VerifyLoginOTPView - Session Key: {request.session.session_key}")
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)


