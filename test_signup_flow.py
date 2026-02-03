from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

from django.conf import settings

def run():
    # Allow testserver for APIClient
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS += ['testserver']

    User = get_user_model()
    email = "test_signup_flow@example.com"
    password = "testpassword123"

    print(f"--- Starting Signup Flow Verification for {email} ---")

    # Cleanup
    User.objects.filter(email=email).delete()
    cache.delete(f'signup_otp_{email}')

    client = APIClient()

    # 1. Signup
    print("\n1. Testing Signup Init (POST /api/v1/auth/signup/)")
    response = client.post('/api/v1/auth/signup/', {'email': email, 'password': password})
    print(f"   Status: {response.status_code}")
    if response.status_code != 201:
        print(f"   FAILED. Response: {response.data}")
        return

    # 2. Check User status
    try:
        user = User.objects.get(email=email)
        print(f"   User Created: {user.email}")
        print(f"   User Is Active: {user.is_active} (Expected: False)")
        if user.is_active:
            print("   FAILED: User should be inactive initially.")
            return
    except User.DoesNotExist:
        print("   FAILED: User object was not created.")
        return

    # 3. Get OTP
    otp = cache.get(f'signup_otp_{email}')
    print(f"\n2. OTP Retrieval")
    print(f"   Retrieved OTP from cache: {otp}")
    if not otp:
        print("   FAILED: OTP not generated/cached.")
        return

    # 4. Verify OTP
    print(f"\n3. Testing Verify Signup (POST /api/v1/auth/signup/verify/) with OTP {otp}")
    response = client.post('/api/v1/auth/signup/verify/', {'email': email, 'otp': otp})
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   FAILED. Response: {response.data}")
        return

    user.refresh_from_db()
    print(f"\n4. Final User Status Check")
    print(f"   User Is Active: {user.is_active} (Expected: True)")
    if not user.is_active:
        print("   FAILED: User should be active after verification.")
        return

    print("\n--- SUCCESS: Signup Flow fully verified! ---")

run()
