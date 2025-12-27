from django.urls import path
from Org import views

urlpatterns = [
    path('check-org/', views.CheckOrganizationExistsView.as_view(), name='check-org'),
]