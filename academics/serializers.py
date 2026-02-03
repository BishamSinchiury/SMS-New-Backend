from rest_framework import serializers
from academics.models import AcademicYear, ClassSection, StudentEnrollment
from Users.serializers import PersonSerializer, StudentSerializer

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current']

class ClassSectionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    teacher_name = serializers.CharField(source='class_teacher.person.full_name', read_only=True)

    class Meta:
        model = ClassSection
        fields = ['id', 'class_name', 'section_name', 'room_number', 'teacher_name']

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.person.full_name', read_only=True)
    class_details = serializers.CharField(source='class_section', read_only=True)

    class Meta:
        model = StudentEnrollment
        fields = ['id', 'academic_year', 'student_name', 'class_details', 'status', 'roll_number']

class AdmissionSerializer(serializers.Serializer):
    person_id = serializers.UUIDField()
    academic_year_id = serializers.IntegerField()
    class_section_id = serializers.IntegerField()
    admission_number = serializers.CharField(max_length=50)
    admission_date = serializers.DateField(required=False)
