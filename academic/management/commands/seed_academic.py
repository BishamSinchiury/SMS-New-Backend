from django.core.management.base import BaseCommand
from academic.models import Faculty, AcademicClass, Subject
from Org.models import Organization
import uuid

class Command(BaseCommand):
    help = 'Seed base academic data for a specific organization'

    def add_arguments(self, parser):
        parser.add_argument('org_id', type=str, help='UUID of the organization')

    def handle(self, *args, **options):
        org_id = options['org_id']
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            self.stderr.write(f"Organization with ID {org_id} does not exist.")
            return

        self.stdout.write(f"Seeding academic data for: {org.org_name}")

        # 1. Faculties
        faculties_data = [
            {'name': 'Science', 'description': 'Faculty of Science and Technology'},
            {'name': 'Management', 'description': 'Faculty of Business and Management'},
            {'name': 'Humanities', 'description': 'Faculty of Social Sciences and Humanities'},
        ]
        
        faculties = {}
        for data in faculties_data:
            faculty, created = Faculty.objects.get_or_create(
                organization=org,
                name=data['name'],
                defaults={'description': data['description']}
            )
            faculties[data['name']] = faculty
            if created:
                self.stdout.write(f"Created Faculty: {faculty.name}")

        # 2. Academic Classes
        classes_data = [
            {'name': 'Class 1', 'level_order': 1},
            {'name': 'Class 2', 'level_order': 2},
            {'name': 'Class 3', 'level_order': 3},
            {'name': 'Class 10', 'level_order': 10},
            {'name': 'Semester 1', 'level_order': 101},
        ]

        classes = {}
        for data in classes_data:
            ac_class, created = AcademicClass.objects.get_or_create(
                organization=org,
                name=data['name'],
                defaults={'level_order': data['level_order']}
            )
            classes[data['name']] = ac_class
            if created:
                self.stdout.write(f"Created Class: {ac_class.name}")

        # 3. Subjects
        subjects_data = [
            {'name': 'Mathematics', 'code': 'MAT101', 'class': 'Class 1'},
            {'name': 'English', 'code': 'ENG101', 'class': 'Class 1'},
            {'name': 'Science', 'code': 'SCI101', 'class': 'Class 1'},
            {'name': 'Physics', 'code': 'PHY101', 'class': 'Class 10'},
            {'name': 'Chemistry', 'code': 'CHE101', 'class': 'Class 10'},
            {'name': 'Programming in C', 'code': 'CS101', 'class': 'Semester 1'},
        ]

        for data in subjects_data:
            ac_class = classes.get(data['class'])
            if ac_class:
                subject, created = Subject.objects.get_or_create(
                    organization=org,
                    name=data['name'],
                    academic_class=ac_class,
                    defaults={'code': data['code']}
                )
                if created:
                    self.stdout.write(f"Created Subject: {subject.name} for {ac_class.name}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded academic data.'))
