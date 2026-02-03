import uuid
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base class for soft-deleting records.
    """
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()


class TenantModel(TimeStampedModel):
    """
    Abstract base class for all multi-tenant models.
    Ensures every object belongs to an Organization.
    """
    # Using string reference 'Org.Organization' to avoid circular imports
    # Assuming the app name is 'Org' based on existing folder structure
    organization = models.ForeignKey(
        'Org.Organization',
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        db_index=True
    )

    class Meta:
        abstract = True
