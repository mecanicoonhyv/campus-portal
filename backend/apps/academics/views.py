from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Course, Section, Enrollment
from .serializers import (
    DepartmentSerializer, CourseSerializer, SectionSerializer,
    EnrollmentSerializer, StudentEnrollmentSerializer
)
from apps.users.models import StudentProfile


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for departments"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'head']
    ordering_fields = ['name']


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for courses"""
    queryset = Course.objects.select_related('department').all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level', 'status']
    search_fields = ['course_id', 'course_name', 'description']
    ordering_fields = ['course_id', 'course_name']


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for sections"""
    queryset = Section.objects.select_related('course', 'instructor', 'room').all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'semester', 'year', 'status', 'instructor']
    search_fields = ['course__course_name', 'instructor_name']
    ordering_fields = ['semester', 'course__course_id']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by instructor for faculty
        if self.request.user.role == 'faculty':
            instructor_id = self.request.query_params.get('my_sections')
            if instructor_id:
                queryset = queryset.filter(instructor__user=self.request.user)

        return queryset


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for enrollments"""
    queryset = Enrollment.objects.select_related(
        'student__user', 'section__course', 'course'
    ).all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'section', 'course', 'semester', 'status']
    ordering_fields = ['-enrollment_date', 'semester']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Students can only see their own enrollments
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = queryset.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return Enrollment.objects.none()

        # Faculty can see enrollments in their sections
        elif user.role == 'faculty':
            section_id = self.request.query_params.get('section')
            if section_id:
                queryset = queryset.filter(
                    section__instructor__user=user,
                    section_id=section_id
                )

        return queryset

    def get_serializer_class(self):
        if self.request.user.role == 'student':
            return StudentEnrollmentSerializer
        return EnrollmentSerializer

    @action(detail=False, methods=['get'])
    def my_enrollments(self, request):
        """Get current student's enrollments"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            enrollments = Enrollment.objects.filter(
                student=student_profile
            ).select_related('section__course', 'course').order_by('-enrollment_date')

            serializer = StudentEnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_grades(self, request):
        """Get current student's grades"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            enrollments = Enrollment.objects.filter(
                student=student_profile,
                grade__isnull=False
            ).exclude(grade='').select_related('section__course', 'course')

            serializer = StudentEnrollmentSerializer(enrollments, many=True)

            # Calculate GPA
            total_points = sum(e.grade_points * e.course.credits for e in enrollments if e.grade_points)
            total_credits = sum(e.course.credits for e in enrollments if e.grade and e.grade not in ['W', 'I'])
            gpa = total_points / total_credits if total_credits > 0 else 0

            return Response({
                'enrollments': serializer.data,
                'gpa': round(float(gpa), 2),
                'total_credits': total_credits
            })
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
