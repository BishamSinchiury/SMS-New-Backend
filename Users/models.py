import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from core.models import TenantModel, TimeStampedModel, SoftDeleteModel

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_claimed', True)
        extra_fields.setdefault('approval_status', 'APPROVED')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Authentication entity. Minimal info.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Hooks for claiming/merging
    is_claimed = models.BooleanField(default=False)

    APPROVAL_STATUS_CHOICES = (
        ('PENDING_PROFILE', 'Pending Profile Setup'),
        ('PENDING_APPROVAL', 'Pending Admin Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    approval_status = models.CharField(
        max_length=20, 
        choices=APPROVAL_STATUS_CHOICES, 
        default='PENDING_PROFILE'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Person(TenantModel, SoftDeleteModel):
    """
    The canonical human entity within an Organization.
    Can be linked to a User (for login) or exist without one.
    """
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='person'
    )
    
    # Personal Details
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150)
    
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, blank=True)
    
    # Contact (Canonical contact for the person)
    personal_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    photo = models.ImageField(upload_to='person_photos/', null=True, blank=True)
    
    # AI Hooks
    ai_profile_summary = models.TextField(blank=True, help_text="AI generated bio/summary")
    embedding_id = models.UUIDField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['phone_number']),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".replace("  ", " ").strip()

    def __str__(self):
        return f"{self.full_name} ({self.organization.name})"


# --- Roles ---

class Student(TenantModel):
    """
    Student Role. Contains academic specific data.
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=50)
    date_of_admission = models.DateField()
    current_status = models.CharField(
        max_length=20, 
        default='ACTIVE',
        choices=[('ACTIVE', 'Active'), ('ALUMNI', 'Alumni'), ('SUSPENDED', 'Suspended')]
    )
    
    # Denormalized current class for easy querying/reporting (Actual history in Enrollment)
    # Using 'academics.ClassSection' string reference to avoid circular imports if defined there
    # For now, we leave it as a logical link to be handled in Academics app or added here if FK needed.
    # Decided: Keep strictly normalized here or add FK to academics later. 
    # Adding a placeholder or managing via Enrollment 'is_active'.
    
    def __str__(self):
        return f"Student: {self.person.full_name} ({self.admission_number})"


class Teacher(TenantModel):
    """
    Teacher Role.
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=50, blank=True)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField()
    qualification = models.TextField(blank=True)
    
    def __str__(self):
        return f"Teacher: {self.person.full_name}"


class Staff(TenantModel):
    """
    Non-teaching Staff Role.
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Staff: {self.person.full_name}"


class Guardian(TenantModel):
    """
    Parent/Guardian Role.
    """
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='guardian_profile')
    occupation = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Guardian: {self.person.full_name}"


class StudentGuardianRelation(TenantModel):
    """
    Many-to-Many link between Student and Guardian with metadata.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardians')
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name='wards')
    relationship = models.CharField(max_length=50, choices=[
        ('FATHER', 'Father'), 
        ('MOTHER', 'Mother'), 
        ('OTHER', 'Other')
    ])
    is_primary_contact = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.guardian} -> {self.student} ({self.relationship})"