from django.core.mail import send_mail
from django.conf import settings

try:
    print(f"Attempting to send email with backend: {settings.EMAIL_BACKEND}")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    
    send_mail(
        'Test Email from Django',
        'This is a test email to verify the configuration.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.EMAIL_HOST_USER], # Send to self for testing
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
