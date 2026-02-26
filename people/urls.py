from django.urls import path, include
from rest_framework.routers import DefaultRouter
from people.views import ProfileSetupView, PersonViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'persons', PersonViewSet, basename='person')
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('profile/setup/', ProfileSetupView.as_view(), name='profile-setup'),
    path('', include(router.urls)),
]
