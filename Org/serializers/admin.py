from rest_framework import serializers
from Org.models import OrganizationAdmin
from Users.serializers import UserSerializer

class OrganizationAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganizationAdmin model.
    Includes user details for nested representation.
    """
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = OrganizationAdmin
        fields = [
            'id', 'user', 'organization', 'role', 
            'is_active', 'created_at', 'updated_at', 'user_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateOrganizationAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating OrganizationAdmin.
    """
    class Meta:
        model = OrganizationAdmin
        fields = ['user', 'organization', 'role', 'is_active']
