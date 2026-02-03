from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonViewSet, UserViewSet
from .views_auth import LoginView, LogoutView, MeView
from .views_otp import GenerateOTPView, VerifyOTPView, SignupView, VerifySignupView
from .views_profile import ProfileSetupView
from .views_admin import UserApprovalViewSet

router = DefaultRouter()
router.register(r'people', PersonViewSet, basename='person')
router.register(r'users', UserViewSet, basename='user')
router.register(r'approvals', UserApprovalViewSet, basename='user-approval')

urlpatterns = [
    # Auth Endpoints
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    
    # Signup Flow
    path('auth/signup/', SignupView.as_view(), name='auth-signup'),
    path('auth/signup/verify/', VerifySignupView.as_view(), name='auth-signup-verify'),
    path('auth/profile-setup/', ProfileSetupView.as_view(), name='auth-profile-setup'),

    # Simple OTP (Login)
    path('auth/otp/generate/', GenerateOTPView.as_view(), name='auth-otp-generate'),
    path('auth/otp/verify/', VerifyOTPView.as_view(), name='auth-otp-verify'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    
    # Existing Router
    path('', include(router.urls)),
]