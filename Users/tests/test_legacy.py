from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from Org.models import Organization
from people.models import Person

User = get_user_model()

class OrgAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test@example.com"
        self.password = "password123"
        
        # Create a default Organization
        self.org = Organization.objects.create(
            org_name="Test Org",
            domain_name="testserver", # Matches default test client host
            email="org@example.com",
            owner=User.objects.create(email="owner@example.com", password="pwd")
        )
        
    def test_signup_allowed(self):
        """Test that signup is allowed"""
        response = self.client.post('/api/v1/auth/signup/', {
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_member_login(self):
        """Test that regular member login works"""
        # Create Member User
        user = User.objects.create_user(email=self.email, password=self.password, organization=self.org)
        Person.objects.create(user=user, organization=self.org, first_name="Test", last_name="User")
        
        # Setup Login OTP
        cache.set(f'login_otp_{self.email}', '123456')
        
        response = self.client.post('/api/v1/auth/login/verify-otp/', {
            'email': self.email,
            'otp': '123456'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_login(self):
        """Test that Admin (Org Owner) login works"""
        admin_user = self.org.owner # The owner
        
        # Setup Login OTP
        cache.set(f'login_otp_{admin_user.email}', '123456')
        
        response = self.client.post('/api/v1/auth/login/verify-otp/', {
            'email': admin_user.email,
            'otp': '123456'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_login(self):
        """Test that Superuser login works"""
        su_user = User.objects.create_superuser(email="su@example.com", password="pwd")
        # Link superuser to org for some tests
        su_user.organization = self.org
        su_user.save()
        
        Person.objects.create(user=su_user, organization=self.org, first_name="Super", last_name="User")
        
        cache.set(f'login_otp_{su_user.email}', '123456')
        
        response = self.client.post('/api/v1/auth/login/verify-otp/', {
            'email': su_user.email,
            'otp': '123456'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
