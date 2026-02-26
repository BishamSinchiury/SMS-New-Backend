import uuid
from django.db import models
from django.conf import settings
from core.models import TenantModel
from simple_history.models import HistoricalRecords

class Person(TenantModel):
    """
    Real-world identity entities. 
    Decouples basic personal data from Authentication (CustomUser).
    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    
    first_name = models.CharField(max_length=255, default="")
    last_name = models.CharField(max_length=255, default="")
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, 
        choices=[
            ('MALE', 'Male'), 
            ('FEMALE', 'Female'), 
            ('OTHER', 'Other'), 
            ('PREFER_NOT_TO_SAY', 'Prefer not to say')
        ], 
        null=True, 
        blank=True
    )
    address = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='person_profile'
    )
    
    is_claimed = models.BooleanField(
        default=False,
        help_text="Designates whether this person has claimed their user account."
    )
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.user and self.organization:
            if self.user.organization != self.organization:
                from django.core.exceptions import ValidationError
                raise ValidationError("Personal profile must belong to the same organization as the user account.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    # Add other student-specific fields here
    
    def __str__(self):
        return f"Student: {self.person}"

class Teacher(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Teacher: {self.person}"

class Employee(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Employee: {self.person}"

class Guardian(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='guardian_profile')
    occupation = models.CharField(max_length=255, blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardians')
    
    def __str__(self):
        return f"Guardian: {self.person}"

class Owner(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='owner_profile')
    # Organization ownership is already handled via CustomUser/Organization relationships,
    # but this model can store additional owner-specific metadata if needed.

    def __str__(self):
        return f"Owner: {self.person}"
