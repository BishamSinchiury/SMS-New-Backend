from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Org.models.organization import Organization, OrganizationDomain

class CheckOrganizationExistsView(APIView):
    """
    Check if an organization exists by domain name (supporting multiple domains).
    """
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        domain_name = request.query_params.get("domain_name")

        if not domain_name:
            return Response(
                {"error": "domain_name query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            domain_record = OrganizationDomain.objects.get(domain=domain_name)
            org = domain_record.organization
            return Response(
                {
                    "organization_exists": True,
                    "name": org.org_name,
                    "email": org.email
                },
                status=status.HTTP_200_OK,
            )
        except OrganizationDomain.DoesNotExist:
            return Response(
                {"detail": "Organization not found for this domain."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        domain_name = request.data.get("domain_name")

        if not domain_name:
            return Response(
                {"error": "domain_name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            domain_record = OrganizationDomain.objects.get(domain=domain_name)
            org = domain_record.organization
            return Response(
                {
                    "organization_exists": True,
                    "name": org.org_name,
                    "email": org.email
                },
                status=status.HTTP_200_OK,
            )
        except OrganizationDomain.DoesNotExist:
            return Response(
                {"detail": "Organization not found for this domain."},
                status=status.HTTP_404_NOT_FOUND,
            )
from rest_framework import viewsets, permissions
from Users.authentication import CsrfExemptSessionAuthentication
from Org.serializers import OrganizationSerializer
from Org.permissions import IsOrganizationAdmin

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    - Superusers: Full global access.
    - System Admins (Owners/Admins): Manage their own organization profile.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
            
        # System admins can only see/manage their own organization
        if user.organization:
            return Organization.objects.filter(id=user.organization.id)
            
        return Organization.objects.none()
