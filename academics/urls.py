from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AcademicYearViewSet, ClassSectionViewSet, AdmissionViewSet

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')
router.register(r'classes', ClassSectionViewSet, basename='class-section')
router.register(r'admissions', AdmissionViewSet, basename='admission')

urlpatterns = [
    path('', include(router.urls)),
]
