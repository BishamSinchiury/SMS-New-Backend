from django.contrib import admin
from .models import Organization, OrganizationProfile

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('org_name', 'domain_name', 'user', 'gmail')
    search_fields = ('org_name', 'domain_name', 'gmail')

@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ('organization', 'slug', 'org_code', 'contact_email')
    search_fields = ('organization__org_name', 'slug', 'org_code', 'contact_email')
