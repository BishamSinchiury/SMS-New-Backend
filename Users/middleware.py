from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class ProfileStatusMiddleware:
    """
    Middleware to enforce profile verification gating.
    Redirects or blocks users based on their approval_status.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 1. Skip System Admins
        if hasattr(request.user, 'is_system_admin') and request.user.is_system_admin:
            return self.get_response(request)

        # 2. Define exempt paths (auth, static, media, and profile setup itself)
        # We use a simple path check for now
        exempt_paths = [
            '/api/v1/auth/',
            '/api/v1/users/me/',
            '/api/v1/users/profile/',
            '/api/v1/profile/',
            '/admin/',
            '/media/',
            '/static/',
        ]
        
        current_path = request.path
        if any(current_path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # 3. Handle Gating Logic for REST API
        # If it's an API request, we don't redirect but let the permission classes handle it.
        # This middleware is primarily for future SSR or to log/track status.
        # However, for now, we follow the requirement to ensure Person exists.
        
        status = request.user.approval_status
        
        # Ensure Person exists (Auto-creation logic mentioned in requirements)
        if not hasattr(request.user, 'person_profile'):
            from people.models.person import Person
            Person.objects.get_or_create(
                user=request.user,
                organization=request.user.organization,
                defaults={
                    'first_name': 'New',
                    'last_name': 'User',
                    'email': request.user.email,
                }
            )

        return self.get_response(request)
