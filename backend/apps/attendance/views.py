from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer, StudentAttendanceSummarySerializer
from apps.users.models import StudentProfile
from apps.academics.models import Enrollment


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for attendance records"""
    queryset = AttendanceRecord.objects.select_related(
        'student__user', 'section__course'
    ).all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'section', 'date', 'status']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Students can only see their own attendance
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = queryset.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return AttendanceRecord.objects.none()

        # Faculty can see attendance for their sections
        elif user.role == 'faculty':
            queryset = queryset.filter(section__instructor__user=user)

        return queryset

    def get_permissions(self):
        """Faculty can create/update attendance, students can only read"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsFaculty()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """Get current student's attendance records"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            records = AttendanceRecord.objects.filter(
                student=student_profile
            ).select_related('section__course').order_by('-date')

            serializer = AttendanceRecordSerializer(records, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_summary(self, request):
        """Get attendance summary by section for current student"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)

            # Get all enrolled sections
            enrollments = Enrollment.objects.filter(
                student=student_profile,
                status='Enrolled'
            ).select_related('section__course')

            summaries = []
            for enrollment in enrollments:
                section = enrollment.section
                records = AttendanceRecord.objects.filter(
                    student=student_profile,
                    section=section
                )

                total = records.count()
                if total > 0:
                    present = records.filter(status='Present').count()
                    absent = records.filter(status='Absent').count()
                    late = records.filter(status='Late').count()
                    excused = records.filter(status='Excused').count()
                    percentage = (present + late) / total * 100

                    summaries.append({
                        'section_id': section.section_id,
                        'course_name': section.course.course_name,
                        'total_classes': total,
                        'present': present,
                        'absent': absent,
                        'late': late,
                        'excused': excused,
                        'attendance_percentage': round(percentage, 2)
                    })

            serializer = StudentAttendanceSummarySerializer(summaries, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class IsFaculty(permissions.BasePermission):
    """Permission class to check if user is faculty"""
    def has_permission(self, request, view):
        return request.user.role == 'faculty'
