from rest_framework import serializers
from .models import Building, Room


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['building_id', 'name', 'address', 'capacity', 'floors',
                  'year_built', 'facilities', 'description']


class RoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = Room
        fields = ['room_id', 'building', 'building_name', 'room_number',
                  'room_type', 'capacity', 'equipment', 'description']
