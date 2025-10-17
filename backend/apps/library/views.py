from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Checkout
from .serializers import BookSerializer, CheckoutSerializer
from apps.users.models import StudentProfile


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for library books"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'author', 'publication_year']


class CheckoutViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for library checkouts"""
    queryset = Checkout.objects.select_related('book', 'student__user').all()
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['book', 'student', 'status']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Students see only their own checkouts
        if user.role == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = queryset.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return Checkout.objects.none()

        return queryset

    @action(detail=False, methods=['get'])
    def my_checkouts(self, request):
        """Get current student's library checkouts"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            checkouts = Checkout.objects.filter(
                student=student_profile
            ).select_related('book').order_by('-checkout_date')

            serializer = CheckoutSerializer(checkouts, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get current student's active checkouts"""
        if request.user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            checkouts = Checkout.objects.filter(
                student=student_profile,
                status__in=['Active', 'Overdue']
            ).select_related('book')

            serializer = CheckoutSerializer(checkouts, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
