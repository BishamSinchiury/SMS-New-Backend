from rest_framework import serializers
from Users.models import Person, CustomUser, Student, Teacher

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_active', 'approval_status', 'last_login']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['admission_number', 'date_of_admission', 'current_status']

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['employee_id', 'designation', 'joining_date', 'qualification']

class PersonSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing/retrieving people.
    """
    user = UserSerializer(read_only=True)
    student_profile = StudentSerializer(read_only=True)
    teacher_profile = TeacherSerializer(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'full_name',
            'gender', 'personal_email', 'phone_number', 'address', 'photo',
            'user', 'student_profile', 'teacher_profile'
        ]

class CreatePersonSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a person. 
    Role creation is handled by the View/Service, this validates Person data.
    """
    class Meta:
        model = Person
        fields = [
            'first_name', 'middle_name', 'last_name', 
            'date_of_birth', 'gender', 'personal_email', 
            'phone_number', 'address'
        ]

class CreateUserForPersonSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    person_id = serializers.UUIDField()
