from rest_framework import serializers
from .models import Department, Course, Section, Enrollment
from apps.facilities.models import Room


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department_id', 'name', 'head', 'phone', 'email', 'building', 'description']


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'department', 'department_name',
                  'credits', 'description', 'prerequisites', 'level', 'status']


class SectionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_credits = serializers.IntegerField(source='course.credits', read_only=True)
    room_name = serializers.SerializerMethodField()
    is_full = serializers.ReadOnlyField()
    available_seats = serializers.ReadOnlyField()

    class Meta:
        model = Section
        fields = ['section_id', 'course', 'course_name', 'course_credits',
                  'section_number', 'semester', 'year', 'instructor_name',
                  'instructor_rank', 'meeting_days', 'meeting_time',
                  'room', 'room_name', 'capacity', 'enrolled', 'status',
                  'is_full', 'available_seats']

    def get_room_name(self, obj):
        return str(obj.room) if obj.room else None


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    section_info = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['enrollment_id', 'student', 'student_name', 'section',
                  'section_info', 'course', 'course_name', 'semester',
                  'enrollment_date', 'status', 'grade', 'grade_points',
                  'credits_attempted', 'credits_earned']
        read_only_fields = ['enrollment_id', 'grade_points']

    def get_section_info(self, obj):
        return f"{obj.section.course.course_id} - {obj.section.section_number}"


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """Detailed enrollment serializer for students"""
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_credits = serializers.IntegerField(source='course.credits', read_only=True)
    section_number = serializers.CharField(source='section.section_number', read_only=True)
    instructor_name = serializers.CharField(source='section.instructor_name', read_only=True)
    meeting_days = serializers.CharField(source='section.meeting_days', read_only=True)
    meeting_time = serializers.CharField(source='section.meeting_time', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['enrollment_id', 'course', 'course_name', 'course_credits',
                  'section', 'section_number', 'instructor_name',
                  'meeting_days', 'meeting_time', 'semester', 'enrollment_date',
                  'status', 'grade', 'grade_points', 'credits_attempted', 'credits_earned']
