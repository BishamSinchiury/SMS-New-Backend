from django.db import transaction
from django.core.exceptions import ValidationError
from Users.models import CustomUser

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user_within_org(email, password, organization, name='', **extra_fields):
        """
        Creates a User associated with an existing Organization.
        """
        if CustomUser.objects.filter(email=email).exists():
             raise ValidationError("User with this email already exists.")
        
        user = CustomUser.objects.create_user(
            email=email, 
            password=password, 
            organization=organization,
            name=name,
            **extra_fields
        )
        return user
