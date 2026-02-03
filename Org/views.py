from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from Org.models import Organization
from Org.serializers import OrganizationSerializer

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

        # In the new model, profile fields are part of Organization.
        # We check if a critical field is filled to determine "has_profile"
        has_profile = bool(org.address and org.contact_email)

        return Response(
            {
                "organization_exists": True,
                "has_profile": has_profile,
                "name": org.name,
                "logo": org.logo.url if org.logo else None
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        domain_name = request.data.get("domain_name")

        if not domain_name:
            return Response(
                {"error": "domain_name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            org = Organization.objects.get(domain_name=domain_name)
        except Organization.DoesNotExist:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # In the new model, profile fields are part of Organization.
        # We check if a critical field is filled to determine "has_profile"
        has_profile = bool(org.address and org.contact_email)

        return Response(
            {
                "organization_exists": True,
                "has_profile": has_profile,
                "name": org.name,
                "logo": org.logo.url if org.logo else None
            },
            status=status.HTTP_200_OK,
        )

class CreateOrganizationProfileView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        domain_name = request.data.get("domain_name")
        if not domain_name:
             return Response({"error": "domain_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            org = Organization.objects.get(domain_name=domain_name)
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)

        if org.address and org.contact_email: # matching logic with CheckOrganizationExistsView
            return Response({"error": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
