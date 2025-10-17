from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import FinancialAid, ParkingPermit, Event
from .serializers import FinancialAidSerializer, ParkingPermitSerializer, EventSerializer
from apps.users.models import StudentProfile


class FinancialAidViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for financial aid"""
    queryset = FinancialAid.objects.select_related('student__user').all()
    serializer_class = FinancialAidSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'type', 'status', 'academic_year', 'semester']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Students see only their own financial aid
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = queryset.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return FinancialAid.objects.none()

        return queryset

    @action(detail=False, methods=['get'])
    def my_aid(self, request):
        """Get current student's financial aid"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            aid_records = FinancialAid.objects.filter(
                student=student_profile
            ).order_by('-disbursement_date')

            serializer = FinancialAidSerializer(aid_records, many=True)

            # Calculate totals
            total_amount = sum(aid.amount for aid in aid_records)
            disbursed = sum(aid.amount for aid in aid_records if aid.status == 'Disbursed')

            return Response({
                'aid_records': serializer.data,
                'total_amount': total_amount,
                'disbursed_amount': disbursed
            })
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ParkingPermitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for parking permits"""
    queryset = ParkingPermit.objects.select_related('student__user').all()
    serializer_class = ParkingPermitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'permit_type', 'status']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Students see only their own permits
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = queryset.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return ParkingPermit.objects.none()

        return queryset

    @action(detail=False, methods=['get'])
    def my_permits(self, request):
        """Get current student's parking permits"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            permits = ParkingPermit.objects.filter(
                student=student_profile
            ).order_by('-issue_date')

            serializer = ParkingPermitSerializer(permits, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for campus events"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'status']
    search_fields = ['name', 'description', 'organizer']
    ordering_fields = ['date', 'name']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        from datetime import date
        events = Event.objects.filter(
            date__gte=date.today(),
            status='Scheduled'
        ).order_by('date')

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
