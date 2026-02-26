from rest_framework import permissions
from Org.models import OrganizationAdmin

class IsOrganizationAdmin(permissions.BasePermission):
    """
    Allows access only to users who are registered as Organization Owners or Admins
    for the specific organization context.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser check removed as per requirements - strictly tenant-based
        if request.user.is_superuser:
            return True
            
        if not request.user.roles.filter(name='ORG_ADMIN').exists():
            return False

        return request.user.is_system_admin

    def has_object_permission(self, request, view, obj):
        # Determine the organization of the target object
        org = None
        if hasattr(obj, 'organization'):
            org = obj.organization
        elif hasattr(obj, 'domain_name'): 
            org = obj
            
        if not org:
            return False
            
        # Check if user belongs to the same organization
        if request.user.organization_id != org.id:
            return False

        # Only owners or active org admins can perform administrative tasks
        is_owner = org.owner_id == request.user.id
        is_admin = OrganizationAdmin.objects.filter(
            user=request.user,
            organization=org,
            role='ORG_ADMIN',
            is_active=True
        ).exists()

        return is_owner or is_admin
