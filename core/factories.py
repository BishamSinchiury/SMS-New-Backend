import uuid
from django.utils import timezone
from Org.models import Organization
from Users.models import CustomUser, Person, Student, Teacher
from academics.models import AcademicYear, ClassLevel, Section, ClassSection, Subject

class FactoryHelper:
    """
    Simple factory to create test data.
    """
    @staticmethod
    def create_org(name="Test Org"):
        return Organization.objects.create(
            name=name,
            slug=f"test-org-{uuid.uuid4().hex[:6]}",
            domain_name=f"test{uuid.uuid4().hex[:6]}.com",
            contact_email="admin@test.com",
            contact_phone="1234567890",
            address="Test Address"
        )

    @staticmethod
    def create_user(email, password="password123"):
        return CustomUser.objects.create_user(email=email, password=password)

    @staticmethod
    def create_person(org, user=None, first_name="John", last_name="Doe", role=None):
        person = Person.objects.create(
            organization=org,
            user=user,
            first_name=first_name,
            last_name=last_name,
            gender='M',
            personal_email=f"{first_name.lower()}.{last_name.lower()}@example.com", 
            phone_number="1234567890"
        )
        if role == 'STUDENT':
            Student.objects.create(
                organization=org,
                person=person,
                admission_number=f"ADM-{uuid.uuid4().hex[:6]}",
                date_of_admission=timezone.now().date()
            )
        elif role == 'TEACHER':
            Teacher.objects.create(
                organization=org,
                person=person,
                designation="Teacher",
                joining_date=timezone.now().date()
            )
        return person

    @staticmethod
    def create_academic_year(org):
        return AcademicYear.objects.create(
            organization=org,
            name="2024-2025",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_current=True
        )

    @staticmethod
    def create_class_section(org, grade="1", section="A"):
        class_level, _ = ClassLevel.objects.get_or_create(organization=org, name=f"Grade {grade}", order=int(grade))
        sec, _ = Section.objects.get_or_create(organization=org, name=section)
        return ClassSection.objects.create(
            organization=org,
            class_level=class_level,
            section=sec
        )
