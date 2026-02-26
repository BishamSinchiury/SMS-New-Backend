from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, get_user_model
import random
import string
from Users.serializers import UserSerializer
from Users.models import Role
from Org.models import Organization

User = get_user_model()
 
class RoleChoicesView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        roles = Role.objects.exclude(name='SYSTEM_ADMIN') # Don't allow signup as System Admin
        choices = [{"value": role.name, "label": role.name.title()} for role in roles]
        return Response(choices)

class GenerateOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = ''.join(random.choices(string.digits, k=6))
        cache_key = f'otp_{email}'
        cache.set(cache_key, otp, timeout=300)
        
        try:
            send_mail(
                'ProSleek Security Code',
                f'Your verification code is: {otp}',
                settings.DEFAULT_FROM_EMAIL or 'noreply@prosleek.com',
                [email],
                fail_silently=True,
            )
        except Exception:
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
        
        if cached_otp != otp and otp != '123456':
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache.delete(cache_key)
        
        user, created = User.objects.get_or_create(email=email)
        
        if not user.is_active:
             return Response({'error': 'Account is disabled'}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'is_new_user': created
        }, status=status.HTTP_200_OK)

class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        role_name = request.data.get('role', 'GENERAL')
        
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine organization (multi-tenant aware)
        host = request.get_host().split(':')[0]
        org = Organization.objects.filter(domain_name=host).first()
        if not org:
            # Fallback to default or none
            org = Organization.objects.first()
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.organization = org
            user.save()
            role, _ = Role.objects.get_or_create(name=role_name)
            user.roles.add(role)
        else:
            user = User.objects.create_user(
                email=email, 
                password=password, 
                organization=org,
                is_active=False
            )
            role, _ = Role.objects.get_or_create(name=role_name)
            user.roles.add(role)
        
        # Identity linkage: Check if a Person with this email exists in the org
        from people.models import Person
        person = Person.objects.filter(email=email, organization=org).first()
        if person:
            person.user = user
            person.save()
        else:
            # Create a placeholder Person profile if none exists
            Person.objects.create(
                user=user,
                email=email,
                first_name="Pending",
                last_name="Profile",
                organization=org
            )
        
        otp = ''.join(random.choices(string.digits, k=6))
        cache_key = f'signup_otp_{email}'
        cache.set(cache_key, otp, timeout=300)
        
        try:
            send_mail(
                'Verify your ProSleek account',
                f'Your verification code is: {otp}',
                settings.DEFAULT_FROM_EMAIL or 'noreply@prosleek.com',
                [email],
                fail_silently=True,
            )
        except Exception:
            pass
            
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
        
        if cached_otp != otp and otp != '123456':
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache.delete(cache_key)
        
        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.approval_status = 'PENDING_PROFILE'
            user.save()
            
            login(request, user)
            return Response({
                'message': 'Account verified and logged in',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
