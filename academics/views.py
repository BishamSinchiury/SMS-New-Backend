from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsTenantUser
from academics.models import AcademicYear, ClassSection, StudentEnrollment
from academics.serializers import (
    AcademicYearSerializer, ClassSectionSerializer, 
    StudentEnrollmentSerializer, AdmissionSerializer
)
from academics.services import AdmissionService
from Users.models import Person

class AcademicYearViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantUser]
    serializer_class = AcademicYearSerializer

    def get_queryset(self):
        return AcademicYear.objects.filter(organization=self.request.user.person.organization)

class ClassSectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantUser]
    serializer_class = ClassSectionSerializer

    def get_queryset(self):
        return ClassSection.objects.filter(organization=self.request.user.person.organization) \
            .select_related('class_level', 'section', 'class_teacher__person')

class AdmissionViewSet(viewsets.ViewSet):
    permission_classes = [IsTenantUser]

    @action(methods=['post'], detail=False)
    def admit(self, request):
        serializer = AdmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            person = Person.objects.get(
                id=serializer.validated_data['person_id'],
                organization=request.user.person.organization
            )
            
            enrollment = AdmissionService.admit_student(
                organization=request.user.person.organization,
                person=person,
                academic_year_id=serializer.validated_data['academic_year_id'],
                class_section_id=serializer.validated_data['class_section_id'],
                admission_number=serializer.validated_data['admission_number'],
                admission_date=serializer.validated_data.get('admission_date')
            )
            
            return Response(
                StudentEnrollmentSerializer(enrollment).data, 
                status=status.HTTP_201_CREATED
            )
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
