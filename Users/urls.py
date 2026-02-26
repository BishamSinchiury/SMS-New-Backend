from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Users.views import (
    UserViewSet, UserManagementViewSet, SystemAdminUserViewSet,
    LoginView, LogoutView, MeView, VerifyLoginOTPView,
    GenerateOTPView, VerifyOTPView, SignupView, VerifySignupView, RoleChoicesView,
    SystemAdminLoginView, SystemAdminVerifyOTPView, ProfileView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'admin/users', UserManagementViewSet, basename='user-management')
router.register(r'sys-admin/users', SystemAdminUserViewSet, basename='sys-admin-user')

urlpatterns = [
    # System Admin Flow (Restricted & Secure)
    path('auth/system/login/', SystemAdminLoginView.as_view(), name='system-auth-login'),
    path('auth/system/login/verify/', SystemAdminVerifyOTPView.as_view(), name='system-auth-verify'),

    # Login Flow
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/login/verify-otp/', VerifyLoginOTPView.as_view(), name='auth-login-verify-otp'),
    
    # Signup Flow
    path('auth/signup/', SignupView.as_view(), name='auth-signup'),
    path('auth/signup/verify/', VerifySignupView.as_view(), name='auth-signup-verify'),
    path('auth/roles/', RoleChoicesView.as_view(), name='auth-roles'),

    # Deprecated OTP endpoints
    path('auth/otp/generate/', GenerateOTPView.as_view(), name='auth-otp-generate'),
    path('auth/otp/verify/', VerifyOTPView.as_view(), name='auth-otp-verify'),
    
    # Common
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    
    # Profile & Verification
    path('profile/me/', ProfileView.as_view(), name='user-profile'),
    
    # Existing Router
    path('', include(router.urls)),
]