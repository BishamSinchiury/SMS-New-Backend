from rest_framework import serializers
from Users.models import CustomUser, Role
from people.serializers import PersonSerializer


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']

class UserSerializer(serializers.ModelSerializer):
    person_profile = PersonSerializer(read_only=True)
    
    roles = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'organization', 'roles', 'is_system_admin', 
            'is_active', 'approval_status', 'last_login', 'person_profile'
        ]

class UserDetailSerializer(serializers.ModelSerializer):
    person_profile = PersonSerializer(read_only=True)
    
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'organization', 'roles', 'is_system_admin', 'is_staff', 'is_active', 
            'approval_status', 'rejection_reason', 'last_login', 'created_at', 'person_profile'
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email']

class SystemAdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    roles = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'roles', 'is_active', 'approval_status']

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        user = CustomUser.objects.create_user(**validated_data)
        if roles:
            user.roles.set(roles)
        return user
