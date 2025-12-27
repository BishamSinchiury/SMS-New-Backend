from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Org.models import  Organization, OrganizationProfile

class CheckOrganizationExistsView(APIView):
    def get(self, request):
        domain_name = request.query_params.get("domain_name")

        if not domain_name:
            return Response(
                {"error": "domain_name query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            org = Organization.objects.get(domain_name=domain_name)
        except Organization.DoesNotExist:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        has_profile = hasattr(org, 'organizationprofile')

        return Response(
            {
                "organization_exists": True,
                "has_profile": has_profile
            },
            status=status.HTTP_200_OK,
        )
