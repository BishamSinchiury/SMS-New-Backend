from rest_framework import serializers
from .models import (
    Faculty, AcademicClass, Course, Subject, 
    Batch, Section, StudentEnrollment, TeacherAssignment
)
from people.serializers import PersonSerializer

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'organization', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'organization', 'created_at']


class AcademicClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicClass
        fields = ['id', 'organization', 'name', 'level_order', 'created_at']
        read_only_fields = ['id', 'organization', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    academic_class_name = serializers.ReadOnlyField(source='academic_class.name')
    faculty_name = serializers.ReadOnlyField(source='faculty.name')

    class Meta:
        model = Course
        fields = [
            'id', 'organization', 'name', 'academic_class', 
            'academic_class_name', 'faculty', 'faculty_name', 'created_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    academic_class_name = serializers.ReadOnlyField(source='academic_class.name')

    class Meta:
        model = Subject
        fields = [
            'id', 'organization', 'name', 'code', 
            'academic_class', 'academic_class_name', 'created_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at']


class BatchSerializer(serializers.ModelSerializer):
    academic_class_name = serializers.ReadOnlyField(source='academic_class.name')

    class Meta:
        model = Batch
        fields = [
            'id', 'organization', 'name', 'academic_class', 
            'academic_class_name', 'start_date', 'end_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at']


class SectionSerializer(serializers.ModelSerializer):
    batch_name = serializers.ReadOnlyField(source='batch.name')
    class_name = serializers.ReadOnlyField(source='batch.academic_class.name')

    class Meta:
        model = Section
        fields = [
            'id', 'organization', 'name', 'batch', 'batch_name', 
            'class_name', 'room_number', 'capacity', 'created_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at']


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student_details = PersonSerializer(source='student', read_only=True)
    section_name = serializers.ReadOnlyField(source='section.name')
    batch_name = serializers.ReadOnlyField(source='section.batch.name')

    class Meta:
        model = StudentEnrollment
        fields = [
            'id', 'organization', 'student', 'student_details', 'section', 
            'section_name', 'batch_name', 'enrollment_date', 'roll_number'
        ]
        read_only_fields = ['id', 'organization', 'enrollment_date']


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    teacher_details = PersonSerializer(source='teacher', read_only=True)
    subject_name = serializers.ReadOnlyField(source='subject.name')
    section_name = serializers.ReadOnlyField(source='section.name')

    class Meta:
        model = TeacherAssignment
        fields = [
            'id', 'organization', 'teacher', 'teacher_details', 'subject', 
            'subject_name', 'section', 'section_name', 'created_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at']
