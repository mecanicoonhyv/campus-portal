from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Building, Room
from .serializers import BuildingSerializer, RoomSerializer


class BuildingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for buildings"""
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['name']


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for rooms"""
    queryset = Room.objects.select_related('building').all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building', 'room_type']
    search_fields = ['room_number', 'building__name']
    ordering_fields = ['building', 'room_number']
