import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from simple_history.models import HistoricalRecords

class Role(TimeStampedModel):
    """
    Dynamic role definitions for authorization.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

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
        extra_fields.setdefault('approval_status', 'APPROVED')
        user = self.create_user(email, password, **extra_fields)
        
        # Identity creation for superuser
        if user.organization:
            from people.models import Person
            Person.objects.create(
                user=user,
                first_name="System",
                last_name="Administrator",
                email=email,
                is_claimed=True,
                organization=user.organization
            )
        
        # Assign SYSTEM_ADMIN role
        role, _ = Role.objects.get_or_create(name='SYSTEM_ADMIN')
        user.roles.add(role)
        
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Authentication entity. Focused strictly on credentials and permissions.
    Personal identity data is stored in the associated 'people.Person' profile.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    organization = models.ForeignKey(
        'Org.Organization', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

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
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection")
    
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    @property
    def is_system_admin(self):
        """
        Check if the user has administrative authority over their organization.
        A "System Admin" is either the Organization Owner OR has the SYSTEM_ADMIN role.
        """
        if not self.organization:
            return False
            
        # Check if owner
        if self.organization.owner_id == self.id:
            return True
            
        # Check for SYSTEM_ADMIN role
        return self.roles.filter(name='SYSTEM_ADMIN').exists()

    # Audit logging
    history = HistoricalRecords()

    def __str__(self):
        return self.email
