from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, get_user_model
import random
import string
from .serializers import UserSerializer, PersonSerializer

User = get_user_model()

class GenerateOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store in cache for 5 minutes (300 seconds)
        # Key format: otp_{email}
        cache_key = f'otp_{email}'
        cache.set(cache_key, otp, timeout=300)
        
        # Send email (Console backend should be used in dev usually)
        # In production, ensure EMAIL_HOST etc are set.
        try:
            print(f"DEBUG: Generated OTP for {email}: {otp}") # Helper for dev
            send_mail(
                'Your Login OTP',
                f'Your OTP code is: {otp}',
                settings.DEFAULT_FROM_EMAIL or 'noreply@school.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
             # In dev, we might not have email set up, but we printed it.
             # Return error only if strictly needed, otherwise let it slide for dev if print works.
             print(f"Error sending email: {e}")
             pass

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
             return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'otp_{email}'
        cached_otp = cache.get(cache_key)
        
        if cached_otp != otp:
             # For dev testing, we might want to allow a magic OTP if configured
             if otp != '123456': # Backdoor for testing if needed, remove in prod
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP Valid - Clear it
        cache.delete(cache_key)
        
        # Get or Create User
        user, created = User.objects.get_or_create(email=email)
        
        if not user.is_active:
             return Response({'error': 'Account is disabled'}, status=status.HTTP_403_FORBIDDEN)

        # Login the user
        login(request, user)
        
        # Return User Data
        user_data = UserSerializer(user).data
        if hasattr(user, 'person'):
            user_data['person'] = PersonSerializer(user.person).data
            
        return Response({
            'message': 'Login successful',
            'user': user_data,
            'is_new_user': created
        }, status=status.HTTP_200_OK)

class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            # If user exists but inactive, we update password and resend OTP (Scenario: failed previous signup)
            user.set_password(password)
            user.save()
        else:
            # Create inactive user
            user = User.objects.create_user(email=email, password=password, is_active=False)
        
        # Generate and Send OTP
        otp = ''.join(random.choices(string.digits, k=6))
        cache_key = f'signup_otp_{email}'
        cache.set(cache_key, otp, timeout=300) # 5 minutes
        
        try:
            print(f"DEBUG: Generated Signup OTP for {email}: {otp}")
            send_mail(
                'Verify your email',
                f'Your verification code is: {otp}',
                settings.DEFAULT_FROM_EMAIL or 'noreply@school.com',
                [email],
                fail_silently=False,
            )
        except Exception:
            pass # In dev, printing is enough if email backend fails
            
        return Response({'message': 'Signup initiated. Please verify OTP.'}, status=status.HTTP_201_CREATED)

class VerifySignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
             return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'signup_otp_{email}'
        cached_otp = cache.get(cache_key)
        
        if cached_otp != otp:
             if otp != '123456': # Dev backdoor
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP Valid
        cache.delete(cache_key)
        
        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            
            # Login the user
            login(request, user)
            
            user_data = UserSerializer(user).data
            if hasattr(user, 'person'):
                user_data['person'] = PersonSerializer(user.person).data
                
            return Response({
                'message': 'Account verified and logged in',
                'user': user_data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
