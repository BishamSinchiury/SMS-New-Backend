from rest_framework import permissions

class IsSystemAdmin(permissions.BasePermission):
    """
    Permission class to restrict access to System Admin users only.
    A System Admin is defined by the is_system_admin property on the CustomUser model.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        return request.user.is_system_admin

class IsSameOrganization(permissions.BasePermission):
    """
    Permission class to ensure a user only accesses data within their own organization.
    Assumes the object has an 'organization' field.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.organization:
            return False
            
        # If the object is the User model itself
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
            
        return False
