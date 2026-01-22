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
    alias = models.CharField(max_length=50, blank=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    pan_vat_number = models.CharField(max_length=50, blank=True, null=True)
    established_date = models.DateField()
    logo = models.ImageField(upload_to='org_logos/', null=True, blank=True)
    theme_color_primary = models.CharField(max_length=7, default='#6366f1')
    theme_color_secondary = models.CharField(max_length=7, default='#ec4899')
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # To be implemented later

    def save(self, *args, **kwargs):
        if not self.alias and self.name:
            # Generate alias: Eastern empire college -> EEC
            words = self.name.split()
            self.alias = "".join([word[0].upper() for word in words if word])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} Profile"