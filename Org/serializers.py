from rest_framework import serializers
from .models import Organization, OrganizationProfile

class OrganizationProfileSerializer(serializers.ModelSerializer):
    theme_color_primary = serializers.CharField(source='primary_color', required=False)
    theme_color_secondary = serializers.CharField(source='secondary_color', required=False)

    class Meta:
        model = OrganizationProfile
        fields = [
            'slug', 'org_code', 'logo', 'primary_color', 'secondary_color',
            'contact_email', 'contact_phone', 'address', 'pan_vat_number',
            'established_date', 'ai_summary', 'theme_color_primary', 'theme_color_secondary'
        ]
        read_only_fields = ['slug', 'org_code']


class OrganizationSerializer(serializers.ModelSerializer):
    profile = OrganizationProfileSerializer(read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'org_name', 'domain_name', 'user', 'gmail', 'profile'
        ]

