from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Org.views import (
    CheckOrganizationExistsView, 
    OrganizationAdminViewSet,
    OrganizationViewSet,
    OrganizationProfileViewSet
)

router = DefaultRouter()
router.register(r'admins', OrganizationAdminViewSet, basename='org-admin')
router.register(r'entities', OrganizationViewSet, basename='organization')

urlpatterns = [
    path('check/', CheckOrganizationExistsView.as_view(), name='check-org'),
    path('profile/', OrganizationProfileViewSet.as_view({
        'get': 'list',
        'patch': 'partial_update',
        'put': 'update'
    }), name='org-profile'),
    path('', include(router.urls)),
]