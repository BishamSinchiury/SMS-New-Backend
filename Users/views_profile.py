from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .serializers import CreatePersonSerializer
from Org.models import Organization
from .models import Person
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileSetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Security Check: Only allow if status is PENDING_PROFILE or REJECTED (retry)
        if user.approval_status not in ['PENDING_PROFILE', 'REJECTED']:
            return Response(
                {'error': 'Profile setup already completed or pending approval.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Resolve Organization
        host = request.get_host().split(':')[0] # Remove port if present
        try:
            # Try exact match first, or 'localhost' fallback for dev if needed
            org = Organization.objects.filter(domain_name=host).first()
            if not org:
                # Fallback for development/testing if no domain matches
                # WARNING: In production, this should be strict.
                org = Organization.objects.first() 
            
            if not org:
                return Response({'error': 'No organization found for this domain.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CreatePersonSerializer(data=request.data)
        if serializer.is_valid():
            # Create or Update Person
            person_data = serializer.validated_data
            
            # Check if person already exists (e.g. retry after rejection)
            person, created = Person.objects.update_or_create(
                user=user,
                defaults={**person_data, 'organization': org}
            )
            
            # Update User Status
            user.approval_status = 'PENDING_APPROVAL'
            user.save()
            
            return Response({
                'message': 'Profile submitted successfully. Pending Admin Approval.',
                'status': user.approval_status
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
