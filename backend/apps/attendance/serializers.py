from rest_framework import serializers
from .models import AttendanceRecord
from apps.academics.models import Section
from apps.users.models import StudentProfile


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_name = serializers.SerializerMethodField()
    section_info = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = ['record_id', 'student', 'student_name', 'section', 'section_info',
                  'course_id', 'course_name', 'date', 'status', 'notes']
        read_only_fields = ['record_id']

    def get_course_name(self, obj):
        return obj.section.course.course_name if obj.section else None

    def get_section_info(self, obj):
        return str(obj.section) if obj.section else None


class StudentAttendanceSummarySerializer(serializers.Serializer):
    """Summary of student's attendance for a section"""
    section_id = serializers.CharField()
    course_name = serializers.CharField()
    total_classes = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
