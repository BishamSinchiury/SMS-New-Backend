from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Faculty, AcademicClass, Course, Subject, 
    Batch, Section, StudentEnrollment, TeacherAssignment
)
from .serializers import (
    FacultySerializer, AcademicClassSerializer, CourseSerializer, 
    SubjectSerializer, BatchSerializer, SectionSerializer, 
    StudentEnrollmentSerializer, TeacherAssignmentSerializer
)
from Org.permissions import IsOrganizationAdmin
from Users.authentication import CsrfExemptSessionAuthentication

class AcademicBaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for Academic models with multi-tenancy support.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return self.queryset.none()
        return self.queryset.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class FacultyViewSet(AcademicBaseViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    search_fields = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()


class AcademicClassViewSet(AcademicBaseViewSet):
    queryset = AcademicClass.objects.all()
    serializer_class = AcademicClassSerializer
    search_fields = ['name']
    ordering_fields = ['level_order']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()


class CourseViewSet(AcademicBaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields = ['academic_class', 'faculty']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()


class SubjectViewSet(AcademicBaseViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filterset_fields = ['academic_class']
    search_fields = ['name', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()


class BatchViewSet(AcademicBaseViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    filterset_fields = ['academic_class', 'is_active']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()


class SectionViewSet(AcademicBaseViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filterset_fields = ['batch', 'batch__academic_class']
    search_fields = ['name', 'room_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()


class StudentEnrollmentViewSet(AcademicBaseViewSet):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    filterset_fields = ['section', 'section__batch', 'student']
    search_fields = ['student__first_name', 'student__last_name', 'roll_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()


class TeacherAssignmentViewSet(AcademicBaseViewSet):
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    filterset_fields = ['teacher', 'subject', 'section']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'subject__name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOrganizationAdmin()]
        return super().get_permissions()
