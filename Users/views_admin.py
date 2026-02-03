from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, PersonSerializer
from .models import Person

User = get_user_model()

class UserApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin ViewSet to manage user approval requests.
    Only Staff/Admin can access this.
    """
    queryset = User.objects.filter(approval_status='PENDING_APPROVAL')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Allow filtering by status if needed, default to pending
        status_param = self.request.query_params.get('status')
        if status_param:
            return User.objects.filter(approval_status=status_param)
        return User.objects.filter(approval_status='PENDING_APPROVAL')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.approval_status = 'APPROVED'
        user.save()
        return Response({'status': 'User approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        user = self.get_object()
        user.approval_status = 'REJECTED'
        user.save()
        return Response({'status': 'User rejected'}, status=status.HTTP_200_OK)
