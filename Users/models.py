from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

class CustomUser(AbstractBaseUser):
    """
    Custom user model for SMS system.
    """
    class UserTypes(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        STAFF = 'STAFF', _('Staff')
        STUDENT = 'STUDENT', _('Student')
    
    user_type = models.CharField(
        max_length=10,
        choices=UserTypes.choices,
        default=UserTypes.STUDENT,
    )
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return f"{self.email} ({self.user_type()}): {self.get_full_name()}"


class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle user creation with email as username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)