from django.contrib.auth import authenticate, login, logout
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from Users.serializers import UserSerializer
from Org.models import Organization, OrganizationAdmin

class SystemAdminLoginView(APIView):
    """
    Step 1 of Admin Login: Password verification and OTP generation.
    Restricted to Organization Owners or active ORG_ADMINs.
    Identifies organization via request domain (Multi-Tenant).
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Identify Organization via Domain
        host = request.get_host().split(':')[0] # Strip port if present
        from Org.models.organization import OrganizationDomain
        
        try:
            # Check primary domain or alternate domains
            organization = Organization.objects.filter(
                models.Q(domain_name=host) | 
                models.Q(domains__domain=host)
            ).distinct().get()
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        except Organization.MultipleObjectsReturned:
            return Response({'error': 'Organization ambiguous'}, status=status.HTTP_409_CONFLICT)

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'Account is disabled'}, status=status.HTTP_403_FORBIDDEN)

        if user.organization_id != organization.id:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        # User must be the owner OR have an active ORG_ADMIN role
        is_owner = organization.owner_id == user.id
        is_org_admin = OrganizationAdmin.objects.filter(
            user=user,
            organization=organization,
            role='ORG_ADMIN',
            is_active=True
        ).exists()

        if not (is_owner or is_org_admin):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        otp = ''.join(random.choices(string.digits, k=6))
        

        # Cache key includes organization ID to prevent cross-tenant OTP reuse
        cache_key = f'admin_otp_{organization.id}_{email}'
        cache.set(cache_key, otp, timeout=180) # 3 minutes
        
        # 5. Send OTP via email
        try:
            send_mail(
                f'Security OTP for {organization.org_name}',
                f'Your secure OTP for admin login to {organization.org_name} is: {otp}. This code expires in 3 minutes.',
                settings.DEFAULT_FROM_EMAIL or 'security@school.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            cache.delete(cache_key)
            return Response(
                {'error': 'Failed to send OTP. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Security OTP sent to your registered email.',
            'email': email,
            'organization': organization.org_name
        }, status=status.HTTP_200_OK)


class SystemAdminVerifyOTPView(APIView):
    """
    Step 2 of Admin Login: OTP verification and Session creation.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        host = request.get_host().split(':')[0]
        try:
            organization = Organization.objects.filter(
                models.Q(domain_name=host) | 
                models.Q(domains__domain=host)
            ).distinct().get()
        except (Organization.DoesNotExist, Organization.MultipleObjectsReturned):
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Validate OTP from Cache
        cache_key = f'admin_otp_{organization.id}_{email}'
        cached_otp = cache.get(cache_key)
        
        if not cached_otp or cached_otp != otp:
        #For Test Purpose only : if cached_otp is None or (cached_otp != otp and otp != '123456'):
            return Response({'error': 'Invalid or expired security code'}, status=status.HTTP_401_UNAUTHORIZED)
        
        cache.delete(cache_key)
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=email, organization=organization, is_active=True)
            
            # Final verify: Owner or active ORG_ADMIN
            is_owner = organization.owner == user
            is_org_admin = OrganizationAdmin.objects.filter(
                user=user,
                organization=organization,
                role='ORG_ADMIN',
                is_active=True
            ).exists()

            if not (is_owner or is_org_admin):
                return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

            login(request, user)
            request.session.set_expiry(3600) 
            

            return Response({
                'message': 'Success',
                'user': UserSerializer(user).data,
                'organization': organization.org_name, 
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            print(f"ERROR: User {email} not found during verification")
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(f"ERROR: Unexpected error in verification: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
