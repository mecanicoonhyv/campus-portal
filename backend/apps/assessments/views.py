from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Assignment, Submission
from .serializers import (
    AssignmentSerializer, SubmissionSerializer, StudentSubmissionSerializer
)
from apps.users.models import StudentProfile
from apps.academics.models import Enrollment


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for assignments"""
    queryset = Assignment.objects.select_related('section__course', 'course').all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['section', 'course', 'type', 'status']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Students see assignments from their enrolled sections
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                enrolled_sections = Enrollment.objects.filter(
                    student=student_profile,
                    status='Enrolled'
                ).values_list('section_id', flat=True)
                queryset = queryset.filter(section_id__in=enrolled_sections)
            except StudentProfile.DoesNotExist:
                return Assignment.objects.none()

        # Faculty see assignments from their sections
        elif user.role == 'faculty':
            queryset = queryset.filter(section__instructor__user=user)

        return queryset

    def get_permissions(self):
        """Only faculty can create/update/delete assignments"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsFaculty()]
        return [permissions.IsAuthenticated()]


class SubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for submissions"""
    queryset = Submission.objects.select_related(
        'assignment__course', 'student__user'
    ).all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assignment', 'student', 'status']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Students see only their own submissions
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = queryset.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return Submission.objects.none()

        # Faculty see submissions for their sections' assignments
        elif user.role == 'faculty':
            queryset = queryset.filter(assignment__section__instructor__user=user)

        return queryset

    def get_serializer_class(self):
        if self.request.user.role == 'student':
            return StudentSubmissionSerializer
        return SubmissionSerializer

    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """Get current student's submissions"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            submissions = Submission.objects.filter(
                student=student_profile
            ).select_related('assignment__course').order_by('-submission_date')

            serializer = StudentSubmissionSerializer(submissions, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch'])
    def grade(self, request, pk=None):
        """Grade a submission (faculty only)"""
        if request.user.role != 'faculty':
            return Response(
                {'detail': 'Only faculty can grade submissions'},
                status=status.HTTP_403_FORBIDDEN
            )

        submission = self.get_object()

        # Verify faculty owns this assignment's section
        if submission.assignment.section.instructor.user != request.user:
            return Response(
                {'detail': 'You can only grade submissions from your sections'},
                status=status.HTTP_403_FORBIDDEN
            )

        points_earned = request.data.get('points_earned')
        feedback = request.data.get('feedback', '')

        if points_earned is not None:
            submission.points_earned = points_earned
            submission.feedback = feedback
            submission.status = 'Graded'
            submission.save()

            serializer = self.get_serializer(submission)
            return Response(serializer.data)

        return Response(
            {'detail': 'points_earned is required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class IsFaculty(permissions.BasePermission):
    """Permission class to check if user is faculty"""
    def has_permission(self, request, view):
        return request.user.role == 'faculty'
