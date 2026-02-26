from django.db import models
import uuid
from core.models import TenantModel
from simple_history.models import HistoricalRecords

class Faculty(TenantModel):
    """
    Branching for classes (e.g., Science, Management, Humanities).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Faculties"
        unique_together = ('organization', 'name')

    def __str__(self):
        return f"{self.name} ({self.organization.org_name})"


class AcademicClass(TenantModel):
    """
    Level definitions (Nursery to PhD).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  # e.g., Class 10, B.Sc. CS, Semester 1
    level_order = models.IntegerField(help_text="Numeric order of the class (e.g., 1 for Nursery, 10 for Class 10)")
    
    history = HistoricalRecords()

    class Meta:
        unique_together = ('organization', 'name')
        ordering = ['level_order']

    def __str__(self):
        return f"{self.name}"


class Course(TenantModel):
    """
    Specific academic programs or curriculum paths linked to classes and faculties.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='courses')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    
    history = HistoricalRecords()

    class Meta:
        unique_together = ('organization', 'name', 'academic_class', 'faculty')

    def __str__(self):
        return f"{self.name} - {self.academic_class.name}"


class Subject(TenantModel):
    """
    Individual subjects/modules assigned to classes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True)
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='subjects')
    
    history = HistoricalRecords()

    class Meta:
        unique_together = ('organization', 'name', 'academic_class')

    def __str__(self):
        return f"{self.name} ({self.academic_class.name})"


class Batch(TenantModel):
    """
    Year/Session cohorts (e.g., 2024 Session).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255) # e.g., Intake 2024, Session 2081
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='batches')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        unique_together = ('organization', 'name', 'academic_class')
        verbose_name_plural = "Batches"

    def __str__(self):
        return f"{self.name} - {self.academic_class.name}"


class Section(TenantModel):
    """
    Multiple sections per Batch (e.g., Section A, Section B).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='sections')
    room_number = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.IntegerField(default=40)
    
    history = HistoricalRecords()

    class Meta:
        unique_together = ('batch', 'name')

    def __str__(self):
        return f"{self.batch.academic_class.name} - {self.batch.name} - {self.name}"


class StudentEnrollment(TenantModel):
    """
    Enrolls a student into a specific section for a batch.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('people.Student', on_delete=models.CASCADE, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    
    history = HistoricalRecords()

    class Meta:
        unique_together = ('section', 'student')
        # Also potentially unique roll number within a section
        # unique_together = [('section', 'student'), ('section', 'roll_number')]

    def __str__(self):
        return f"{self.student.first_name} in {self.section}"


class TeacherAssignment(TenantModel):
    """
    Assigns a teacher to a specific subject within a section.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey('people.Teacher', on_delete=models.CASCADE, related_name='teacher_assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_assignments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='teacher_assignments')
    
    history = HistoricalRecords()

    class Meta:
        unique_together = ('section', 'subject', 'teacher')

    def __str__(self):
        return f"{self.teacher.first_name} teaches {self.subject.name} in {self.section}"
