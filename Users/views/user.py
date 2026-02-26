from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from Users.models import CustomUser
from Users.serializers import (
    UserSerializer, UserDetailSerializer, UserUpdateSerializer, SystemAdminUserCreateSerializer
)
from Users.permissions import IsSystemAdmin, IsSameOrganization
from people.models.person import Person
from people.serializers import PersonSerializer
from Users.authentication import CsrfExemptSessionAuthentication

class ProfileView(APIView):
    """
    Self-service profile management for the authenticated user.
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        person = Person.objects.filter(
            user=request.user,
            organization=request.user.organization
        ).first()
        
        if not person:
            return Response(
                {'error': 'Profile not found. Please create your profile.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(PersonSerializer(person).data)

    def post(self, request):
        return self.update_profile(request)

    def put(self, request):
        return self.update_profile(request)

    def patch(self, request):
        return self.update_profile(request)

    def update_profile(self, request):
        person, created = Person.objects.get_or_create(
            user=request.user,
            organization=request.user.organization
        )
        serializer = PersonSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(is_claimed=True)
            
            # Update user status if necessary
            user = request.user
            if user.approval_status in ['PENDING_PROFILE', 'REJECTED']:
                user.approval_status = 'PENDING_APPROVAL'
                user.rejection_reason = None
                user.save()
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Standard user viewset for authenticated users.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)



from Org.permissions import IsOrganizationAdmin

class UserManagementViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for full user CRUD operations.
    Multi-tenant aware: restricted to Organization System Admins.
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsOrganizationAdmin]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        # Admins can only see users within their own organization
        if not user.organization:
            return CustomUser.objects.none()
            
        queryset = CustomUser.objects.filter(organization=user.organization)
        
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(approval_status=status_param)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = self.get_object()
        role = request.data.get('role')
        
        if not role:
            return Response(
                {'error': 'A role must be assigned during approval.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        from Users.models import Role
        try:
            role_obj = Role.objects.get(name=role)
        except Role.DoesNotExist:
            return Response(
                {'error': f'Role "{role}" does not exist.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.approval_status = 'APPROVED'
        user.roles.add(role_obj)
        user.rejection_reason = None
        user.save()

        # Update associated Person claim status
        if hasattr(user, 'person_profile'):
            person = user.person_profile
            person.is_claimed = True
            person.save()

        return Response(
            {'status': 'User approved', 'role': role}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        user = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        user.approval_status = 'REJECTED'
        user.rejection_reason = reason
        user.save()
        return Response({'status': 'User rejected', 'reason': reason}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response({'status': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)

class SystemAdminUserViewSet(viewsets.ModelViewSet):
    """
    Dedicated ViewSet for System Admins to manage user approvals.
    Strictly restricted to Organization Owners or ORG_ADMINs.
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsSystemAdmin, IsSameOrganization]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_serializer_class(self):
        if self.action == 'create':
            return SystemAdminUserCreateSerializer
        return UserDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return CustomUser.objects.none()
        
        # Admins can only manage users in their organization
        queryset = CustomUser.objects.filter(organization=user.organization)
        
        # Filtering
        status_param = self.request.query_params.get('status')
        
        if status_param:
            queryset = queryset.filter(approval_status=status_param)
            
        return queryset

    def perform_create(self, serializer):
        # Enforce organization on creation
        serializer.save(organization=self.request.user.organization)

    def perform_update(self, serializer):
        # Ensure organization remains the same and cannot be changed by the admin
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['patch'], url_path='approval')
    def approval(self, request, pk=None):
        """
        Handle user approval or rejection.
        PATCH /api/sys-admin/users/{id}/approval/
        """
        user = self.get_object()
        approval_status = request.data.get('approval_status')
        rejection_reason = request.data.get('rejection_reason')

        if not approval_status:
            return Response(
                {'error': 'approval_status is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if approval_status == 'APPROVED':
            user.approval_status = 'APPROVED'
            user.rejection_reason = None
            # Auto-claim person profile if exists
            if hasattr(user, 'person_profile'):
                person = user.person_profile
                person.is_claimed = True
                person.save()
        elif approval_status == 'REJECTED':
            if not rejection_reason:
                return Response(
                    {'error': 'rejection_reason is required for REJECTED status.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.approval_status = 'REJECTED'
            user.rejection_reason = rejection_reason
        else:
            return Response(
                {'error': 'Invalid approval_status. Choose APPROVED or REJECTED.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user.save()
        return Response({
            'message': f'User {approval_status.lower()} successfully.',
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)

from rest_framework.views import APIView

class MeView(APIView):
    """
    Consolidated Me endpoint as per requirements.
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserDetailSerializer(request.user).data)
