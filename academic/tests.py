from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from Org.models import Organization
from academic.models import Faculty, AcademicClass, Course, Subject, Batch, Section, StudentEnrollment, TeacherAssignment
from people.models.person import Person
import uuid

User = get_user_model()

class AcademicModuleTest(TestCase):
    def setUp(self):
        # Create Org A
        self.owner_a = User.objects.create_user(email="owner_a@test.com", password="password")
        self.org_a = Organization.objects.create(org_name="Org A", owner=self.owner_a, email="org_a@test.com")
        self.owner_a.organization = self.org_a
        self.owner_a.save()

        # Create Org B
        self.owner_b = User.objects.create_user(email="owner_b@test.com", password="password")
        self.org_b = Organization.objects.create(org_name="Org B", owner=self.owner_b, email="org_b@test.com")
        self.owner_b.organization = self.org_b
        self.owner_b.save()

    def test_multi_tenancy_isolation(self):
        """
        Verify that academic entities are isolated by organization.
        """
        # Create faculties in different orgs
        Faculty.objects.create(organization=self.org_a, name="Science")
        Faculty.objects.create(organization=self.org_b, name="Management")

        # Org A should only see Science
        self.assertEqual(Faculty.objects.filter(organization=self.org_a).count(), 1)
        self.assertEqual(Faculty.objects.filter(organization=self.org_a).first().name, "Science")

        # Org B should only see Management
        self.assertEqual(Faculty.objects.filter(organization=self.org_b).count(), 1)
        self.assertEqual(Faculty.objects.filter(organization=self.org_b).first().name, "Management")

    def test_unique_constraints_per_org(self):
        """
        Verify that unique constraints apply within an organization but allow same names across orgs.
        """
        Faculty.objects.create(organization=self.org_a, name="Science")
        Faculty.objects.create(organization=self.org_b, name="Science") # Allowed across orgs

        with self.assertRaises(IntegrityError):
            Faculty.objects.create(organization=self.org_a, name="Science") # Blocked within same org

    def test_hierarchical_relationships(self):
        """
        Verify the Faculty -> Course -> Class -> Batch -> Section hierarchy.
        """
        faculty = Faculty.objects.create(organization=self.org_a, name="Science")
        ac_class = AcademicClass.objects.create(organization=self.org_a, name="Grade 11", level_order=11)
        course = Course.objects.create(organization=self.org_a, name="Pre-Medical", academic_class=ac_class, faculty=faculty)
        batch = Batch.objects.create(
            organization=self.org_a, 
            name="2024 Session", 
            academic_class=ac_class,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        section = Section.objects.create(batch=batch, name="Section A")

        self.assertEqual(course.faculty, faculty)
        self.assertEqual(batch.academic_class, ac_class)
        self.assertEqual(section.batch, batch)
        self.assertEqual(section.batch.academic_class, ac_class)

    def test_enrollment_and_assignment(self):
        """
        Verify student enrollment and teacher assignment logic.
        """
        # Create People
        student_p = Person.objects.create(
            organization=self.org_a,
            first_name="John", last_name="Doe", email="john@test.com",
            person_type='STUDENT', is_claimed=True
        )
        teacher_p = Person.objects.create(
            organization=self.org_a,
            first_name="Jane", last_name="Smith", email="jane@test.com",
            person_type='TEACHER', is_claimed=True
        )

        # Setup Structure
        ac_class = AcademicClass.objects.create(organization=self.org_a, name="Grade 10", level_order=10)
        batch = Batch.objects.create(
            organization=self.org_a, name="2024", academic_class=ac_class,
            start_date="2024-01-01", end_date="2024-12-31"
        )
        section = Section.objects.create(batch=batch, name="Section A")
        subject = Subject.objects.create(organization=self.org_a, name="Mathematics", academic_class=ac_class)

        # Enroll Student
        enrollment = StudentEnrollment.objects.create(
            organization=self.org_a,
            student=student_p,
            section=section,
            roll_number="101"
        )
        
        # Assign Teacher
        assignment = TeacherAssignment.objects.create(
            organization=self.org_a,
            teacher=teacher_p,
            subject=subject,
            section=section
        )

        self.assertEqual(StudentEnrollment.objects.filter(section=section).count(), 1)
        self.assertEqual(TeacherAssignment.objects.filter(section=section, subject=subject).count(), 1)
        self.assertEqual(enrollment.student, student_p)
        self.assertEqual(assignment.teacher, teacher_p)
