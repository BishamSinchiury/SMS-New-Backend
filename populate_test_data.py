import os
import django
import sys
from datetime import date

# Add the project directory to the sys.path
sys.path.append('/home/bisham-sinchiury/Code/SMS new/Backend')

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms.settings')

# Setup Django
django.setup()

from Org.models import Organization
from Users.models import CustomUser, Person

def populate():
    # 1. Create Organization for localhost
    domain = 'localhost'
    org_name = 'Localhost Test School'
    
    org, created = Organization.objects.get_or_create(
        domain_name=domain,
        defaults={
            'name': org_name,
            'slug': 'localhost-school',
            'org_code': 'LOCALHOST001',
            'contact_email': 'admin@localhost.com',
            'contact_phone': '555-0123',
            'address': '123 Localhost Lane, Cyber City',
            'established_date': date(2020, 1, 1),
            'primary_color': '#6366f1',
        }
    )
    
    if created:
        print(f"✅ Created Organization: {org.name} ({domain})")
    else:
        print(f"ℹ️ Organization already exists: {org.name} ({domain})")
        # Ensure address is set so 'has_profile' returns True
        if not org.address:
            org.address = '123 Localhost Lane, Cyber City'
            org.save()
            print(f"✅ Updated Organization address.")

    # 2. Create Admin User
    email = 'admin@localhost.com'
    password = 'password123'
    
    try:
        user = CustomUser.objects.get(email=email)
        print(f"ℹ️ User {email} already exists.")
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_superuser(email=email, password=password)
        print(f"✅ Created Superuser: {email} / {password}")

    # 3. Create Person Profile linked to User and Org
    if not hasattr(user, 'person'):
        Person.objects.create(
            organization=org,
            user=user,
            first_name='Admin',
            last_name='User',
            gender='O',
            personal_email=email,
            phone_number='555-ADMIN'
        )
        print(f"✅ Created Person profile for {email}")
    else:
        print(f"ℹ️ Person profile already exists for {email}")

if __name__ == '__main__':
    populate()
