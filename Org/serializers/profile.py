from rest_framework import serializers
from Org.models.organization import OrganizationProfile

class OrganizationProfileSerializer(serializers.ModelSerializer):
    organization_name = serializers.ReadOnlyField(source='organization.org_name')

    class Meta:
        model = OrganizationProfile
        fields = [
            'id', 'organization', 'organization_name', 'description', 
            'address', 'phone_number', 'website', 'logo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'organization_name', 'created_at', 'updated_at']
