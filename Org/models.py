from django.db import models

# Create your models here.
class Organization(models.Model):
    domain_name = models.CharField(max_length=255, unique=True)
    org_id = models.CharField(max_length=100, unique=True)
    org_password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain_name
    
class OrganizationProfile(models.Model):
    organization = models.OneToOneField(
        Organization, 
        on_delete=models.CASCADE,
        related_name='organizationprofile')
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    established_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} Profile"