from django.urls import path
from .views import CheckOrganizationExistsView, CreateOrganizationProfileView

urlpatterns = [
    path('check/', CheckOrganizationExistsView.as_view(), name='check-org'),
    path('', CreateOrganizationProfileView.as_view(), name='create-profile'),
]