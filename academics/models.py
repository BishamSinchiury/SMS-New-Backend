import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TenantModel, TimeStampedModel

class AcademicYear(TenantModel):
    """
    Defines the academic calendar (e.g., 2023-2024).
    """
    name = models.CharField(max_length=20, help_text="e.g. 2023-2024")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one active year per organization
            AcademicYear.objects.filter(
                organization=self.organization, 
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClassLevel(TenantModel):
    """
    Represents a definition of a Grade/Standard (e.g., Grade 1, Grade 10).
    """
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(help_text="For sorting, e.g. 1 for Grade 1")
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Section(TenantModel):
    """
    Represents a division within a class level (e.g., A, B, C).
    """
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name


class Subject(TenantModel):
    """
    A subject taught (e.g., Mathematics, Physics).
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    is_elective = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class ClassSection(TenantModel):
    """
    Combines ClassLevel and Section (e.g., Grade 1 - A).
    This is the physical unit of students.
    """
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey('Users.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='class_teacher_of')
    
    # Capacity management
    room_number = models.CharField(max_length=20, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['organization', 'class_level', 'section'], name='unique_class_section_per_org')
        ]

    def __str__(self):
        return f"{self.class_level} - {self.section}"


class StudentEnrollment(TenantModel):
    """
    Tracks a student's history in a specific class for a specific year.
    Crucial for historical reporting.
    """
    ENROLLMENT_STATUS = (
        ('STUDYING', 'Studying'),
        ('PROMOTED', 'Promoted'),
        ('FAILED', 'Failed'),
        ('DROPPED', 'Dropped'),
    )

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    student = models.ForeignKey('Users.Student', on_delete=models.CASCADE, related_name='enrollments')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    
    roll_number = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='STUDYING')
    
    # Historical Snapshot (optional, for fast reporting without joining)
    date_enrolled = models.DateField()
    date_left = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('academic_year', 'student') 
        # A student can strictly be in one class per year (normally)

    def __str__(self):
        return f"{self.student} in {self.class_section} ({self.academic_year})"


class TeacherSubjectAssignment(TenantModel):
    """
    Links a teacher to a subject in a specific class section for a year.
    """
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    teacher = models.ForeignKey('Users.Teacher', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    
    is_primary_teacher = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.teacher} -> {self.subject} in {self.class_section}"


class Exam(TenantModel):
    """
    An assessment event.
    """
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="e.g. Midterm 2024")
    start_date = models.DateField()
    end_date = models.DateField()
    
    # AI Hook: Summary of overall class performance
    ai_performance_summary = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ExamResult(TenantModel):
    """
    Granular marks for a student in a subject for an exam.
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student_enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student_enrollment.student} - {self.subject}: {self.marks_obtained}"


class Attendance(TenantModel):
    """
    Daily attendance record.
    Often high volume, so kept minimal.
    """
    date = models.DateField()
    student_enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('P', 'Present'), ('A', 'Absent'), ('L', 'Late')])
    remarks = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['date', 'status']),
        ]


class Feedback(TenantModel):
    """
    Feedback loop between Student and Teacher.
    """
    student = models.ForeignKey('Users.Student', on_delete=models.CASCADE)
    teacher = models.ForeignKey('Users.Teacher', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    comment = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    # AI sentiment analysis hook
    ai_sentiment_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Feedback from {self.student} to {self.teacher}"
