from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile, FacultyProfile, StaffProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone',
                  'role', 'date_of_birth', 'address', 'city', 'state', 'zip_code']
        read_only_fields = ['id']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for Student Profile"""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'student_id', 'enrollment_date', 'major',
                  'year_level', 'gpa', 'status', 'emergency_contact',
                  'emergency_phone', 'full_name']
        read_only_fields = ['id', 'student_id']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class FacultyProfileSerializer(serializers.ModelSerializer):
    """Serializer for Faculty Profile"""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = FacultyProfile
        fields = ['id', 'user', 'faculty_id', 'department', 'rank', 'hire_date',
                  'office_building', 'office_number', 'specialization', 'status',
                  'education', 'years_experience', 'research_areas', 'publications',
                  'is_professor', 'full_name']
        read_only_fields = ['id', 'faculty_id', 'salary']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for Staff Profile"""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = StaffProfile
        fields = ['id', 'user', 'staff_id', 'department', 'position', 'hire_date',
                  'office_building', 'office_number', 'status', 'full_name']
        read_only_fields = ['id', 'staff_id', 'salary']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with role-specific profile"""
    student_profile = StudentProfileSerializer(read_only=True)
    faculty_profile = FacultyProfileSerializer(read_only=True)
    staff_profile = StaffProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone',
                  'role', 'date_of_birth', 'address', 'city', 'state', 'zip_code',
                  'student_profile', 'faculty_profile', 'staff_profile']
        read_only_fields = ['id', 'username', 'email', 'role']
