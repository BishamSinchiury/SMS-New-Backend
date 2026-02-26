import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel

class Organization(TimeStampedModel, SoftDeleteModel):
    """
    The root tenant entity. Represents an Organization in the SaaS system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_name = models.CharField(max_length=255, help_text="Legal name of the organization")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_organizations'
    )
    email = models.EmailField(help_text="Primary contact email")
    
    # Audit logging (if simple-history is installed and desired here too)
    # history = HistoricalRecords()

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.org_name

class OrganizationDomain(TimeStampedModel):
    """
    Separate domains linked to an Organization.
    Solves the localhost vs 127.0.0.1 issue.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='domains'
    )
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.domain} -> {self.organization.org_name}"

class OrganizationProfile(TimeStampedModel):
    """
    Extended profile information for an Organization.
    One-to-one relation to the Organization model.
    """
    organization = models.OneToOneField(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='org_logos/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Organization Profile"
        verbose_name_plural = "Organization Profiles"

    def __str__(self):
        return f"Profile for {self.organization.org_name}"
