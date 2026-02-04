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
from Users.serializers import UserSerializer, PersonSerializer

class LoginView(APIView):
    authentication_classes = [] # Allow unauthenticated access
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        print(f"DEBUG: Login attempt for email: {email}") # DEBUG
        
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user with email + password
        user = authenticate(request, username=email, password=password)
        
        print(f"DEBUG: Authenticate result: {user}") # DEBUG

        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({'error': 'Account is not activated. Please check your email for verification.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Generate OTP for 2FA
        otp = ''.join(random.choices(string.digits, k=6))
        cache_key = f'login_otp_{email}'
        cache.set(cache_key, otp, timeout=300) # 5 minutes
        
        # Send OTP via email
        try:
            print(f"DEBUG: Generated Login OTP for {email}: {otp}") # DEBUG
            send_mail(
                'Your Login OTP',
                f'Your OTP code for login is: {otp}',
                settings.DEFAULT_FROM_EMAIL or 'noreply@school.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
            pass # In dev, printing is enough if email backend fails
        
        return Response({
            'message': 'OTP sent to your email. Please verify to complete login.',
            'email': email
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
        
        if cached_otp != otp:
            # Dev backdoor for testing
            if otp != '123456':
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP Valid - Clear it
        cache.delete(cache_key)
        
        # Get user and login
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=email)
            
            if not user.is_active:
                return Response({'error': 'Account is not activated'}, status=status.HTTP_403_FORBIDDEN)
            
            # Login the user
            login(request, user)
            
            # Serialize User + Person
            user_data = UserSerializer(user).data
            if hasattr(user, 'person'):
                user_data['person'] = PersonSerializer(user.person).data
            
            return Response({
                'message': 'Login successful',
                'user': user_data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        if hasattr(user, 'person'):
                user_data['person'] = PersonSerializer(user.person).data
        return Response(user_data)
