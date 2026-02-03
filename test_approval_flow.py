from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from django.conf import settings
from Users.models import Person

def run():
    # Allow testserver
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS += ['testserver']

    User = get_user_model()
    email = "approval_test_user@example.com"
    password = "password123"
    
    # Clean up
    User.objects.filter(email=email).delete()
    cache.delete(f'signup_otp_{email}')
    
    # Create Test Org
    from Org.models import Organization
    org, _ = Organization.objects.get_or_create(
        domain_name='testserver',
        defaults={
            'name': 'Test School',
            'slug': 'test-school',
            'contact_email': 'info@test.com',
            'contact_phone': '123',
            'address': 'Test Addr',
            'org_code': 'TEST001'
        }
    )

    client = APIClient()

    print(f"--- Starting Approval Workflow Verification for {email} ---")

    # 1. Signup & Verify (Reusing known flow)
    print("\n1. Signup & OTP Verify")
    client.post('/api/v1/auth/signup/', {'email': email, 'password': password})
    otp = cache.get(f'signup_otp_{email}')
    client.post('/api/v1/auth/signup/verify/', {'email': email, 'otp': otp})
    
    user = User.objects.get(email=email)
    print(f"   Status after Signup: {user.approval_status} (Expected: PENDING_PROFILE)")
    if user.approval_status != 'PENDING_PROFILE': print("   FAILED Step 1"); return

    # 2. Profile Setup
    print("\n2. Profile Setup (POST /api/v1/auth/profile-setup/)")
    # We need to be logged in. The verify endpoint logs us in, but let's force auth header just in case or rely on session
    client.force_authenticate(user=user) 
    
    profile_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'date_of_birth': '2000-01-01',
        'gender': 'M',
        'phone_number': '1234567890',
        'address': '123 Test St'
    }
    resp = client.post('/api/v1/auth/profile-setup/', profile_data)
    print(f"   Response: {resp.status_code}")
    if resp.status_code != 200: print(f"   FAILED Step 2: {resp.data}"); return

    user.refresh_from_db()
    print(f"   Status after Profile: {user.approval_status} (Expected: PENDING_APPROVAL)")
    print(f"   Person Created: {Person.objects.filter(user=user).exists()}")
    if user.approval_status != 'PENDING_APPROVAL': print("   FAILED Step 2 status"); return

    # 3. Admin Approval
    print("\n3. Admin Approval (POST /api/v1/approvals/{id}/approve/)")
    admin = User.objects.create_superuser('admin_tester@example.com', 'adminpass')
    client.force_authenticate(user=admin)
    
    resp = client.post(f'/api/v1/approvals/{user.id}/approve/')
    print(f"   Response: {resp.status_code}")
    
    user.refresh_from_db()
    print(f"   Status after Admin Action: {user.approval_status} (Expected: APPROVED)")
    if user.approval_status != 'APPROVED': print("   FAILED Step 3"); return

    print("\n--- SUCCESS: Full Approval Workflow Verified! ---")

run()
