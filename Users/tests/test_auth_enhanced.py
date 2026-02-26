import io
import uuid
from PIL import Image
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from Org.models import Organization
from people.models import Person, Student
from Users.models import Role

User = get_user_model()

def generate_test_image():
    file = io.BytesIO()
    image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file

class EnhancedAuthFlowTests(APITestCase):
    def setUp(self):
        # Create a default Organization
        self.owner = User.objects.create_user(email="owner@example.com", password="password123")
        self.org = Organization.objects.create(
            org_name="Test Org",
            domain_name="testserver",
            email="org@example.com",
            owner=self.owner
        )
        self.owner.organization = self.org
        self.owner.save()
        
        # Identity for owner
        Person.objects.create(user=self.owner, organization=self.org, first_name="Owner", last_name="User")
        
        # Roles
        self.admin_role, _ = Role.objects.get_or_create(name='ORG_ADMIN')
        self.student_role, _ = Role.objects.get_or_create(name='STUDENT')
        
        # Approval logic uses SYSTEM_ADMIN or ORG_ADMIN usually
        self.owner.roles.add(self.admin_role)

    def test_complete_auth_lifecycle(self):
        """
        Tests: Signup -> Profile Setup -> Admin Approval -> Login
        """
        # 1. Signup
        signup_data = {
            'email': 'student@example.com',
            'password': 'password123',
            'role': 'STUDENT'
        }
        response = self.client.post('/api/v1/auth/signup/', signup_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(email='student@example.com')
        self.assertEqual(user.approval_status, 'PENDING_PROFILE')
        
        # 2. Login (should work but be gated by middleware/status if we had strict UI gating)
        # Setup Login OTP
        cache.set(f'login_otp_{user.email}', '123456')
        response = self.client.post('/api/v1/auth/login/verify-otp/', {
            'email': user.email,
            'otp': '123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Force authentication for subsequent requests in this test process
        self.client.force_authenticate(user=user)
        
        # 3a. Upload Photo (multipart)
        photo_data = {
            'photo': SimpleUploadedFile('profile.png', generate_test_image().read(), content_type='image/png')
        }
        response = self.client.patch('/api/v1/profile/me/', photo_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3b. Setup Extensions (JSON)
        setup_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'MALE',
            'address': '123 Street',
            'student_profile': {
                'admission_number': 'S12345'
            }
        }
        response = self.client.post('/api/v1/people/profile/setup/', setup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertEqual(user.approval_status, 'PENDING_APPROVAL')
        person = user.person_profile
        self.assertEqual(person.first_name, 'John')
        self.assertTrue(person.photo.name.startswith('profile_photos/'))
        
        # 4. Admin Approval
        self.client.force_authenticate(user=self.owner)
        approval_data = {
            'role': 'STUDENT'
        }
        # Using UserManagementViewSet.approve action
        response = self.client.post(f'/api/v1/admin/users/{user.id}/approve/', approval_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertEqual(user.approval_status, 'APPROVED')
        self.assertTrue(user.roles.filter(name='STUDENT').exists())
        person.refresh_from_db()
        self.assertTrue(person.is_claimed)
        
        # Verify Student Extension was created
        self.assertTrue(hasattr(person, 'student_profile'))

    def test_admin_rejection_and_resubmission(self):
        """
        Tests: Profile Setup -> Admin Rejection -> Profile Update -> Moves back to PENDING_APPROVAL
        """
        user = User.objects.create_user(email="rejected@example.com", password="password123", organization=self.org)
        user.approval_status = 'PENDING_APPROVAL'
        user.save()
        Person.objects.create(user=user, organization=self.org, first_name="Lazy", last_name="User")

        # Admin Rejection
        self.client.force_authenticate(user=self.owner)
        rejection_data = {'reason': 'Invalid photo'}
        response = self.client.post(f'/api/v1/admin/users/{user.id}/reject/', rejection_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertEqual(user.approval_status, 'REJECTED')
        self.assertEqual(user.rejection_reason, 'Invalid photo')
        
        # User Resubmission
        self.client.force_authenticate(user=user)
        resubmission_data = {'first_name': 'Corrected Name'}
        response = self.client.patch('/api/v1/profile/me/', resubmission_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertEqual(user.approval_status, 'PENDING_APPROVAL')
        self.assertIsNone(user.rejection_reason)

    def test_user_activation_deactivation(self):
        """Test activating and deactivating a user account"""
        user = User.objects.create_user(email="toggle@example.com", password="password123", organization=self.org)
        self.client.force_authenticate(user=self.owner)
        
        # Deactivate
        response = self.client.patch(f'/api/v1/admin/users/{user.id}/', {'is_active': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
        # Activate
        response = self.client.patch(f'/api/v1/admin/users/{user.id}/', {'is_active': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_person_crud(self):
        """Test Person profile CRUD via PersonViewSet"""
        self.client.force_authenticate(user=self.owner)
        
        # Create
        person_data = {
            'first_name': 'Manual',
            'last_name': 'Person',
            'email': 'manual@person.com'
        }
        response = self.client.post('/api/v1/people/persons/', person_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        person_id = response.data['id']
        
        # Retrieve
        response = self.client.get(f'/api/v1/people/persons/{person_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Manual')
        
        # Update
        response = self.client.patch(f'/api/v1/people/persons/{person_id}/', {'last_name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Person.objects.get(id=person_id).last_name, 'Updated')
        
        # Delete
        response = self.client.delete(f'/api/v1/people/persons/{person_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Person.objects.filter(id=person_id).exists())

    def test_user_crud_as_admin(self):
        """Test full User CRUD by Organization Admin"""
        self.client.force_authenticate(user=self.owner)
        
        # Create
        user_data = {
            'email': 'manual@example.com',
            'password': 'password123',
            'roles': ['STUDENT']
        }
        # Correct URL: /api/v1/sys-admin/users/ (with trailing slash)
        response = self.client.post('/api/v1/sys-admin/users/', user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_user_id = response.data['id']
        
        # Update
        update_data = {'approval_status': 'APPROVED'}
        response = self.client.patch(f'/api/v1/sys-admin/users/{new_user_id}/approval/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(f'/api/v1/admin/users/{new_user_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email='manual@example.com').exists())
