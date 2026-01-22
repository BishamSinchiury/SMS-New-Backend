from rest_framework import serializers
from .models import OrganizationProfile

class OrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationProfile
        fields = [
            'name', 'alias', 'address', 'latitude', 'longitude', 
            'contact_email', 'contact_phone', 'pan_vat_number', 
            'established_date', 'logo', 'theme_color_primary', 
            'theme_color_secondary'
        ]
        read_only_fields = ['alias'] # Alias is auto-generated if not provided, but we might want to allow editing? Ideally auto-gen on backend.

    def create(self, validated_data):
        # We need to associate the profile with the organization from the request context
        # But for now, since we don't have auth fully set up for "Org Admin", 
        # we might need to pass the domain or org_id to link it.
        # However, the user is likely not logged in yet as an Org Admin? 
        # OR this is the first step of setup.
        
        # Assumption: The frontend sends the domain_name to identify which Org this profile belongs to.
        # In a real scenario, this endpoint should be protected or use a temporary token.
        # For this MVP, we will pass 'domain_name' in the context or request data.
        
        return super().create(validated_data)
