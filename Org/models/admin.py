import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from .organization import Organization

class OrganizationAdminManager(models.Manager):
    """
    Manager to simplify creation and management of OrgAdmins.
    """
    def create_admin(self, user, organization, role='ORG_ADMIN'):
        admin, created = self.get_or_create(
            user=user,
            organization=organization,
            defaults={'role': role}
        )
        return admin

class OrganizationAdmin(TimeStampedModel):
    """
    Represents organization-level administrators.
    Multi-tenant aware by linking a CustomUser to an Organization as an Admin.
    """
    ROLE_CHOICES = (
        ('ORG_ADMIN', 'Organization Admin'),
        ('DEPT_ADMIN', 'Department Admin'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='org_admin_roles'
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='admins'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ORG_ADMIN')
    is_active = models.BooleanField(default=True)

    objects = OrganizationAdminManager()
    
    # Audit logging
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organization'], 
                name='unique_org_admin'
            )
        ]
        verbose_name = "Organization Admin"
        verbose_name_plural = "Organization Admins"

    def __str__(self):
        return f"{self.user.email} - {self.organization.org_name} ({self.role})"
