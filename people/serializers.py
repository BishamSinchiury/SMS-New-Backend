from rest_framework import serializers
from people.models import Person, Student, Teacher, Employee, Guardian, Owner


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['admission_number']

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['employee_id', 'specialization']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employee_id', 'department', 'designation']

class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ['occupation']

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = []

class PersonSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    enrollment_summary = serializers.SerializerMethodField()
    
    student_profile = StudentSerializer(read_only=True)
    teacher_profile = TeacherSerializer(read_only=True)
    employee_profile = EmployeeSerializer(read_only=True)
    guardian_profile = GuardianSerializer(read_only=True)
    owner_profile = OwnerSerializer(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'photo',
            'phone_number', 'date_of_birth', 'gender', 'address',
            'is_claimed', 'is_active',
            'user_id', 'user_email',
            'student_profile', 'teacher_profile', 'employee_profile', 
            'guardian_profile', 'owner_profile',
            'enrollment_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_claimed', 'created_at', 'updated_at',
                            'user_email', 'user_id', 'full_name', 'enrollment_summary']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

    def get_user_id(self, obj):
        return str(obj.user.id) if obj.user else None

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_enrollment_summary(self, obj):
        """Returns list of batch/section enrollments for this person (if Student)."""
        try:
            if hasattr(obj, 'student_profile'):
                enrollments = obj.student_profile.enrollments.select_related(
                    'section__batch__academic_class'
                ).all()
                return [
                    {
                        'enrollment_id': str(e.id),
                        'section': e.section.name,
                        'batch': e.section.batch.name,
                        'class': e.section.batch.academic_class.name,
                        'roll_number': e.roll_number,
                    }
                    for e in enrollments
                ]
        except Exception:
            pass
        return []
