from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from Org.models import OrganizationAdmin, Organization
from Org.serializers import OrganizationAdminSerializer, CreateOrganizationAdminSerializer
from Users.authentication import CsrfExemptSessionAuthentication
from Org.permissions import IsOrganizationAdmin
from core.mixins import TenantSafeQuerySetMixin

class OrganizationAdminViewSet(TenantSafeQuerySetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing Organization Administrators.
    Uses TenantSafeQuerySetMixin to ensure admins can only see/manage 
    admins within their own organization context.
    """
    queryset = OrganizationAdmin.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateOrganizationAdminSerializer
        return OrganizationAdminSerializer

    def perform_create(self, serializer):
        user = self.request.user
        organization = serializer.validated_data.get('organization')
        
        # Security Check: Only superusers or existing active admins of the 
        # target organization can add new admins.
        if not user.is_superuser:
            is_authorized = OrganizationAdmin.objects.filter(
                user=user, 
                organization=organization, 
                is_active=True
            ).exists()
            if not is_authorized:
                raise PermissionDenied("You do not have permission to manage admins for this organization.")
                
        serializer.save()

    @action(detail=False, methods=['get'], url_path='my-organizations')
    def my_organizations(self, request):
        """
        List organizations where the current user holds an administrative role.
        """
        user = request.user
        if user.is_superuser:
            orgs = Organization.objects.all()
        else:
            admin_org_ids = OrganizationAdmin.objects.filter(
                user=user, 
                is_active=True
            ).values_list('organization_id', flat=True)
            orgs = Organization.objects.filter(id__in=admin_org_ids)
            
        from Org.serializers import OrganizationSerializer
        serializer = OrganizationSerializer(orgs, many=True)
        return Response(serializer.data)
