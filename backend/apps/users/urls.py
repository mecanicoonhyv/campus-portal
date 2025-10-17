from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, StudentProfileViewSet, FacultyProfileViewSet, StaffProfileViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'students', StudentProfileViewSet, basename='student')
router.register(r'faculty', FacultyProfileViewSet, basename='faculty')
router.register(r'staff', StaffProfileViewSet, basename='staff')

urlpatterns = [
    path('', include(router.urls)),
]
