from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from Org.models import Organization, OrganizationProfile
from Org.serializers import OrganizationSerializer, OrganizationProfileSerializer
from django.utils.text import slugify
import uuid

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

        # In the new model, profile fields are part of OrganizationProfile.
        try:
            profile = org.profile
            has_profile = True
            logo_url = profile.logo.url if profile.logo else None
        except OrganizationProfile.DoesNotExist:
            profile = None
            has_profile = False
            logo_url = None

        return Response(
            {
                "organization_exists": True,
                "has_profile": has_profile,
                "name": org.org_name,
                "logo": logo_url
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

        try:
            profile = org.profile
            has_profile = True
            logo_url = profile.logo.url if profile.logo else None
        except OrganizationProfile.DoesNotExist:
            profile = None
            has_profile = False
            logo_url = None

        return Response(
            {
                "organization_exists": True,
                "has_profile": has_profile,
                "name": org.org_name,
                "logo": logo_url
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

        if hasattr(org, 'profile'):
            return Response({"error": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrganizationProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Auto-generate required fields if not present (though they likely aren't in data due to read_only)
            # slug and org_code logic
            slug = slugify(org.org_name)
            # Ensure slug uniqueness
            base_slug = slug
            counter = 1
            while OrganizationProfile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            org_code = str(uuid.uuid4())[:8].upper()
            
            serializer.save(organization=org, slug=slug, org_code=org_code)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

