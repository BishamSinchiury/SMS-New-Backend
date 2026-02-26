from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions, parsers
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from Org.models.organization import OrganizationProfile
from Org.serializers.profile import OrganizationProfileSerializer
from Users.authentication import CsrfExemptSessionAuthentication
from Users.permissions import IsSystemAdmin

class OrganizationProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Organization Profile Management.
    Strictly restricted to System Admins of the same organization.
    """
    serializer_class = OrganizationProfileSerializer
    permission_classes = [IsSystemAdmin]
    authentication_classes = [CsrfExemptSessionAuthentication]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        user = self.request.user
        print(f"DEBUG: OrganizationProfileViewSet.get_queryset - User: {user}, Org: {user.organization if hasattr(user, 'organization') else 'No Org'}")
        if not hasattr(user, 'organization') or not user.organization:
            return OrganizationProfile.objects.none()
        
        # Ensure the profile exists, create if not
        profile, created = OrganizationProfile.objects.get_or_create(
            organization=user.organization
        )
        return OrganizationProfile.objects.filter(organization=user.organization)

    def get_object(self):
        user = self.request.user
        print(f"DEBUG: OrganizationProfileViewSet.get_object - User: {user}, Org: {user.organization if hasattr(user, 'organization') else 'No Org'}")
        profile, created = OrganizationProfile.objects.get_or_create(
            organization=user.organization
        )
        return profile

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # We use a 1-to-1 relation, so creation is handled via get_or_create in get_object/list
        # This method can be used for updating via POST if preferred, or just return 405
        return Response(
            {'error': 'Method not allowed. Use PATCH or PUT to update profile.'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
