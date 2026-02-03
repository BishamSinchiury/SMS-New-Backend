from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from academics.models import StudentEnrollment, ClassSection, AcademicYear
from Users.models import Student, Person

class AdmissionService:
    @staticmethod
    @transaction.atomic
    def admit_student(organization, person, academic_year_id, class_section_id, admission_number, admission_date=None):
        """
        Admit a student:
        1. Create Student role for Person (if not exists).
        2. Create Enrollment for the Academic Year.
        """
        if admission_date is None:
            admission_date = timezone.now().date()

        # 1. Create/Get Student Role
        student, created = Student.objects.get_or_create(
            person=person,
            organization=organization,
            defaults={
                'admission_number': admission_number,
                'date_of_admission': admission_date,
                'current_status': 'ACTIVE'
            }
        )
        if not created and student.current_status != 'ACTIVE':
            student.current_status = 'ACTIVE'
            student.save()

        # 2. Create Enrollment
        try:
            enrollment = StudentEnrollment.objects.create(
                organization=organization,
                academic_year_id=academic_year_id,
                student=student,
                class_section_id=class_section_id,
                date_enrolled=admission_date,
                status='STUDYING'
            )
        except IntegrityError:
            raise ValidationError("Student is already enrolled in this academic year.")
            
        return enrollment

class PromotionService:
    @staticmethod
    @transaction.atomic
    def promote_students(organization, student_ids, next_year_id, next_class_section_id):
        """
        Bulk promote students.
        """
        promoted_enrollments = []
        for student_id in student_ids:
            # Check if already enrolled in next year
            if StudentEnrollment.objects.filter(
                organization=organization,
                academic_year_id=next_year_id,
                student_id=student_id
            ).exists():
                continue # Skip if already promoted
            
            enrollment = StudentEnrollment.objects.create(
                organization=organization,
                academic_year_id=next_year_id,
                student_id=student_id,
                class_section_id=next_class_section_id,
                date_enrolled=timezone.now().date(),
                status='STUDYING'
            )
            promoted_enrollments.append(enrollment)
            
            # Update previous enrollment status to PROMOTED if needed? 
            # Ideally we find the previous active enrollment and set status='PROMOTED'
            
        return promoted_enrollments
