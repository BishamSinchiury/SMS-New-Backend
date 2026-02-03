from rest_framework import serializers
from .models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    theme_color_primary = serializers.CharField(source='primary_color', required=False)
    theme_color_secondary = serializers.CharField(source='secondary_color', required=False)

    class Meta:
        model = Organization
        fields = [
            'name', 'slug', 'address', 
            'contact_email', 'contact_phone', 'pan_vat_number', 
            'established_date', 'logo', 'theme_color_primary', 
            'theme_color_secondary'
        ]
        read_only_fields = ['slug']
