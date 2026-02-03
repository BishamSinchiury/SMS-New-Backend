from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsTenantUser
from core.pagination import StandardResultsSetPagination
from Users.models import Person, CustomUser
from Users.serializers import (
    PersonSerializer, CreatePersonSerializer, 
    CreateUserForPersonSerializer, UserSerializer
)
from Users.services import PersonService, UserService

class PersonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']

    def get_queryset(self):
        # Enforce Multi-tenancy
        return Person.objects.filter(
            organization=self.request.user.person.organization
        ).select_related('user', 'student_profile', 'teacher_profile')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreatePersonSerializer
        return PersonSerializer

    def perform_create(self, serializer):
        # Use Service if complex, otherwise standard save with org
        serializer.save(organization=self.request.user.person.organization)


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [IsTenantUser]
    
    @action(methods=['post'], detail=False, url_path='create-for-person')
    def create_for_person(self, request):
        serializer = CreateUserForPersonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            person = Person.objects.get(
                id=serializer.validated_data['person_id'], 
                organization=request.user.person.organization
            )
            user = UserService.create_user_for_person(
                person, 
                serializer.validated_data['email'], 
                serializer.validated_data['password']
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
