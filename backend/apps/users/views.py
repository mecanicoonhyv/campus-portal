from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import StudentProfile, FacultyProfile, StaffProfile
from .serializers import (
    UserSerializer, UserDetailSerializer, StudentProfileSerializer,
    FacultyProfileSerializer, StaffProfileSerializer
)

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """Custom permission to only allow owners of an object or admins to access it"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user profiles"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'me':
            return UserDetailSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for student profiles"""
    queryset = StudentProfile.objects.select_related('user').all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or user.role == 'faculty':
            return StudentProfile.objects.select_related('user').all()
        if user.role == 'student':
            return StudentProfile.objects.filter(user=user)
        return StudentProfile.objects.none()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current student's profile"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = StudentProfile.objects.select_related('user').get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class FacultyProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for faculty profiles"""
    queryset = FacultyProfile.objects.select_related('user').all()
    serializer_class = FacultyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return FacultyProfile.objects.select_related('user').all()
        if user.role == 'faculty':
            return FacultyProfile.objects.filter(user=user)
        # Students and others can view basic faculty info
        return FacultyProfile.objects.select_related('user').all()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current faculty member's profile"""
        if request.user.role != 'faculty':
            return Response(
                {'detail': 'Only faculty members can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = FacultyProfile.objects.select_related('user').get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except FacultyProfile.DoesNotExist:
            return Response(
                {'detail': 'Faculty profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class StaffProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for staff profiles"""
    queryset = StaffProfile.objects.select_related('user').all()
    serializer_class = StaffProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return StaffProfile.objects.select_related('user').all()
        if user.role == 'staff':
            return StaffProfile.objects.filter(user=user)
        return StaffProfile.objects.none()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current staff member's profile"""
        if request.user.role != 'staff':
            return Response(
                {'detail': 'Only staff members can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = StaffProfile.objects.select_related('user').get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except StaffProfile.DoesNotExist:
            return Response(
                {'detail': 'Staff profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
