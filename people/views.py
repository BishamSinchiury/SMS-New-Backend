from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from people.models import Person, Student, Teacher, Employee, Guardian, Owner
from Users.models import CustomUser, Role
from Users.authentication import CsrfExemptSessionAuthentication
from people.serializers import PersonSerializer
from Org.permissions import IsOrganizationAdmin
from academic.models import StudentEnrollment, Section
from academic.serializers import StudentEnrollmentSerializer


from people.serializers import (
    PersonSerializer, StudentSerializer, TeacherSerializer, 
    EmployeeSerializer, GuardianSerializer, OwnerSerializer
)

class ProfileSetupView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            person = Person.objects.get(user=request.user)
        except Person.DoesNotExist:
            return Response({'error': 'Person profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            serializer = PersonSerializer(person, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                user = request.user
                user_roles = user.roles.all().values_list('name', flat=True)
                data = request.data

                # Handle profile extensions
                if 'STUDENT' in user_roles:
                    profile, _ = Student.objects.get_or_create(person=person)
                    if 'student_profile' in data:
                        ext_serializer = StudentSerializer(profile, data=data['student_profile'], partial=True)
                        if ext_serializer.is_valid():
                            ext_serializer.save()
                        else:
                            transaction.set_rollback(True)
                            return Response(ext_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                if 'TEACHER' in user_roles:
                    profile, _ = Teacher.objects.get_or_create(person=person)
                    if 'teacher_profile' in data:
                        ext_serializer = TeacherSerializer(profile, data=data['teacher_profile'], partial=True)
                        if ext_serializer.is_valid():
                            ext_serializer.save()
                        else:
                            transaction.set_rollback(True)
                            return Response(ext_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                if 'STAFF' in user_roles:
                    profile, _ = Employee.objects.get_or_create(person=person)
                    if 'employee_profile' in data:
                        ext_serializer = EmployeeSerializer(profile, data=data['employee_profile'], partial=True)
                        if ext_serializer.is_valid():
                            ext_serializer.save()
                        else:
                            transaction.set_rollback(True)
                            return Response(ext_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                if 'GUARDIAN' in user_roles:
                    profile, _ = Guardian.objects.get_or_create(person=person)
                    if 'guardian_profile' in data:
                        ext_serializer = GuardianSerializer(profile, data=data['guardian_profile'], partial=True)
                        if ext_serializer.is_valid():
                            ext_serializer.save()
                        else:
                            transaction.set_rollback(True)
                            return Response(ext_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                if 'ADMIN' in user_roles or 'SYSTEM_ADMIN' in user_roles:
                    Owner.objects.get_or_create(person=person)

                user.approval_status = 'PENDING_APPROVAL'
                user.rejection_reason = None
                user.save()

                return Response({
                    'message': 'Profile updated. Awaiting admin approval.',
                    'person': PersonSerializer(person).data
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for People (students, teachers, staff, etc.) within the organization.
    Supports filtering by person_type (STUDENT, TEACHER, STAFF, ...), search, and ordering.

    Extra actions:
      POST   /{id}/link-user/    — Link a CustomUser account to this Person
      DELETE /{id}/link-user/    — Unlink the user account from this Person
    """
    serializer_class = PersonSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_claimed', 'gender']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['first_name']

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return Person.objects.none()
        return Person.objects.filter(organization=user.organization).select_related('user')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'link_user']:
            return [IsOrganizationAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post', 'delete'], url_path='link-user')
    def link_user(self, request, pk=None):
        """
        POST: Link a CustomUser (by user_id) to this Person.
        DELETE: Unlink the user from this Person.
        """
        person = self.get_object()

        if request.method == 'DELETE':
            if person.user:
                person.user = None
                person.is_claimed = False
                person.save()
                return Response({'message': 'User account unlinked.'})
            return Response({'error': 'No user linked to this person.'}, status=status.HTTP_400_BAD_REQUEST)

        # POST: link user
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = CustomUser.objects.get(
                id=user_id,
                organization=request.user.organization
            )
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found in your organization.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure this user isn't already linked to another Person
        if hasattr(target_user, 'person_profile') and target_user.person_profile and target_user.person_profile.id != person.id:
            return Response(
                {'error': f'User {target_user.email} is already linked to another person.'},
                status=status.HTTP_409_CONFLICT
            )

        person.user = target_user
        person.is_claimed = True
        person.save()

        return Response({
            'message': f'User {target_user.email} linked successfully.',
            'person': PersonSerializer(person).data
        })


class StudentViewSet(PersonViewSet):
    """
    CRUD for Students only — pre-filtered to person_type=STUDENT.

    Inherits all PersonViewSet endpoints including link-user.
    Extra actions:
      POST   /{id}/enroll/    — Enroll student into a section
      DELETE /{id}/enroll/    — Remove an existing enrollment
    """

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return Person.objects.none()
        # Filter people who have a Student profile extension
        return Person.objects.filter(
            organization=user.organization,
            student_profile__isnull=False
        ).select_related('user', 'student_profile')

    def perform_create(self, serializer):
        with transaction.atomic():
            person = serializer.save(organization=self.request.user.organization)
            # Automatically create Student extension when creating via StudentViewSet
            Student.objects.get_or_create(person=person)

    @action(detail=True, methods=['post', 'delete'], url_path='enroll')
    def enroll(self, request, pk=None):
        """
        POST: Enroll this student into a section.
              Body: { "section": "<uuid>", "roll_number": "S001" (optional) }

        DELETE: Remove an existing enrollment.
                Body: { "enrollment_id": "<uuid>" }
        """
        student = self.get_object()

        if request.method == 'DELETE':
            enrollment_id = request.data.get('enrollment_id')
            if not enrollment_id:
                return Response(
                    {'error': 'enrollment_id is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                enrollment = StudentEnrollment.objects.get(
                    id=enrollment_id,
                    student=student.student_profile,
                    organization=request.user.organization
                )
                enrollment.delete()
                return Response({'message': 'Enrollment removed successfully.'})
            except StudentEnrollment.DoesNotExist:
                return Response(
                    {'error': 'Enrollment not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # POST: create enrollment
        section_id = request.data.get('section')
        if not section_id:
            return Response(
                {'error': 'section is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            section = Section.objects.get(
                id=section_id,
                organization=request.user.organization
            )
        except Section.DoesNotExist:
            return Response(
                {'error': 'Section not found in your organization.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check duplicate
        if StudentEnrollment.objects.filter(student=student.student_profile, section=section).exists():
            return Response(
                {'error': 'Student is already enrolled in this section.'},
                status=status.HTTP_409_CONFLICT
            )

        roll_number = request.data.get('roll_number', '')
        enrollment = StudentEnrollment.objects.create(
            student=student.student_profile,
            section=section,
            roll_number=roll_number,
            organization=request.user.organization
        )

        return Response({
            'message': 'Student enrolled successfully.',
            'enrollment': StudentEnrollmentSerializer(enrollment).data
        }, status=status.HTTP_201_CREATED)
