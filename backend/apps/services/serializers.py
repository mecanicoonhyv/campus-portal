from rest_framework import serializers
from .models import FinancialAid, ParkingPermit, Event


class FinancialAidSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialAid
        fields = ['aid_id', 'student', 'student_name', 'type', 'name',
                  'amount', 'academic_year', 'semester', 'status',
                  'disbursement_date', 'description']


class ParkingPermitSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = ParkingPermit
        fields = ['permit_id', 'student', 'student_name', 'permit_type',
                  'lot_number', 'vehicle_make', 'vehicle_model', 'vehicle_year',
                  'license_plate', 'issue_date', 'expiration_date', 'status',
                  'is_expired']


class EventSerializer(serializers.ModelSerializer):
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ['event_id', 'name', 'type', 'description', 'date',
                  'start_time', 'end_time', 'location', 'organizer',
                  'capacity', 'registered', 'status', 'is_full', 'available_spots']
