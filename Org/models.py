import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, TenantModel, SoftDeleteModel

class Organization(TimeStampedModel, SoftDeleteModel):
    """
    The root tenant entity. Represents a School or Educational Institution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_name = models.CharField(max_length=255, help_text="Legal name of the organization")
    domain_name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizations')
    gmail = models.EmailField(help_text="primary gmail of organization")
    
    class Meta:
        indexes = [
            models.Index(fields=['domain_name']),
        ]

    def __str__(self):
        return self.org_name


class OrganizationProfile(TimeStampedModel, SoftDeleteModel):
    """
    Profile details for an Organization.
    """
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='profile')
    
    slug = models.SlugField(max_length=255, unique=True, help_text="Unique URL identifier")
    
    # Legacy/Existing fields support (mapped or kept if needed)
    org_code = models.CharField(max_length=100, unique=True, help_text="Unique code for internal reference")
    
    # Configuration & Branding
    logo = models.ImageField(upload_to='org_logos/')
    primary_color = models.CharField(max_length=7, default='#6366f1')
    secondary_color = models.CharField(max_length=7, default='#ec4899')
    
    # Contact Info
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    
    # Legal
    pan_vat_number = models.CharField(max_length=50)
    established_date = models.DateField()

    # AI & Analytics Hooks
    ai_summary = models.JSONField(
        default=dict, 
        help_text="AI-generated summary of the organization state/stats."
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"Profile of {self.organization.org_name}"


class SubOrganization(TenantModel, SoftDeleteModel):
    """
    Branches, Campuses, or Departments within an Organization.
    Some might have separate legal standing, others just modification.
    """
    SUB_ORG_TYPES = (
        ('CAMPUS', 'Campus'),
        ('BRANCH', 'Branch'),
        ('DEPT', 'Department'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=SUB_ORG_TYPES, default='BRANCH')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    address = models.TextField(blank=True)
    is_legal_entity = models.BooleanField(default=False, help_text="Does this branch have its own legal registration?")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class OrganizationDocument(TenantModel):
    """
    Compliance documents, SOPs, Licenses.
    Metadata only; files stored in object storage ( S3).
    """
    DOC_TYPES = (
        ('LICENSE', 'License'),
        ('REGISTRATION', 'Registration Certificate'),
        ('SOP', 'Standard Operating Procedure'),
        ('CONTRACT', 'Contract'),
        ('OTHER', 'Other'),
    )

    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOC_TYPES)
    file_url = models.URLField(help_text="External storage URL (S3)")
    version = models.CharField(max_length=20, default='1.0')
    
    expiry_date = models.DateField(null=True, blank=True)
    is_active_version = models.BooleanField(default=True)
    
    ai_extracted_text = models.TextField(blank=True, help_text="OCR or text extraction for search")
    embedding_id = models.UUIDField(null=True, blank=True, help_text="Reference to vector DB embedding")

    def __str__(self):
        return f"{self.title} (v{self.version})"