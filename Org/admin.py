from django.contrib import admin
from .models import Organization, OrganizationAdmin

@admin.register(Organization)
class OrganizationModelAdmin(admin.ModelAdmin):
    list_display = ('org_name', 'domain_name', 'owner', 'email', 'created_at')
    search_fields = ('org_name', 'domain_name', 'email')
    list_filter = ('created_at',)

@admin.register(OrganizationAdmin)
class OrganizationAdminRegistration(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'organization')
    search_fields = ('user__email', 'organization__org_name')

from .models import OrganizationProfile

@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ('organization', 'phone_number', 'website', 'updated_at')
    search_fields = ('organization__org_name', 'phone_number', 'website')
