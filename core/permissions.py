from rest_framework import permissions

class IsTenantUser(permissions.BasePermission):
    """
    Allows access only to users who belong to the organization
    associated with the requested object or context.
    """

    def has_permission(self, request, view):
        # 1. User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # 2. User must be associated with an Organization or be a Superuser
        if request.user.is_superuser:
            return True
            
        if not request.user.organization:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        user_org = request.user.organization
        
        # Check if object has 'organization' attribute
        if hasattr(obj, 'organization'):
            return obj.organization == user_org
            
        # Check if object is the Organization itself
        from Org.models import Organization
        if isinstance(obj, Organization):
             return obj == user_org

        return False

class IsApprovedOrProfileOnly(permissions.BasePermission):
    """
    Strictly gates access based on CustomUser.approval_status.
    - System Admins: Bypass all restrictions.
    - APPROVED: Full access.
    - PENDING/REJECTED: Allow ONLY profile-related endpoints.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # 1. System Admin bypass
        if hasattr(request.user, 'is_system_admin') and request.user.is_system_admin:
            return True
            
        # 2. Approved user full access
        if request.user.approval_status == 'APPROVED':
            return True
            
        # 3. Restricted access for others: Allow only profile endpoints
        # We check the view's name or a custom attribute if needed, 
        # but for simplicity, we check the request path.
        allowed_paths = [
            '/api/v1/users/me/',
            '/api/v1/users/profile/',
            '/api/v1/auth/logout/',
        ]
        
        if any(request.path.startswith(p) for p in allowed_paths):
            return True
            
        return False
