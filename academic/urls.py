from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FacultyViewSet, AcademicClassViewSet, CourseViewSet, 
    SubjectViewSet, BatchViewSet, SectionViewSet, 
    StudentEnrollmentViewSet, TeacherAssignmentViewSet
)

router = DefaultRouter()
router.register(r'faculties', FacultyViewSet)
router.register(r'classes', AcademicClassViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'batches', BatchViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'enrollments', StudentEnrollmentViewSet)
router.register(r'assignments', TeacherAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
