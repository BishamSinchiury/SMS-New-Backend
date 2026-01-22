from django.urls import path
from .views import CheckOrganizationExistsView, CreateOrganizationProfileView

urlpatterns = [
    path('check-org/', CheckOrganizationExistsView.as_view(), name='check-org'),
    path('create-profile/', CreateOrganizationProfileView.as_view(), name='create-profile'),
]