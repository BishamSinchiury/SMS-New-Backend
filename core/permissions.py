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
            
        # 2. User must have a linked Person profile with an Organization
        if not hasattr(request.user, 'person') or not request.user.person.organization:
            return False

        # 3. Check for specific Organization Header (optional enforcement)
        # org_id = request.headers.get('X-ORG-ID')
        # if org_id and str(request.user.person.organization.id) != org_id:
        #    return False

        return True

    def has_object_permission(self, request, view, obj):
        # The object must belong to the same organization as the user
        user_org = request.user.person.organization
        
        # Check if object has 'organization' attribute
        if hasattr(obj, 'organization'):
            return obj.organization == user_org
            
        # Check if object is the Organization itself
        if hasattr(obj, 'domain_name'): # heuristic for Organization model
             return obj == user_org

        return False
