from rest_framework import serializers
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    section_info = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Assignment
        fields = ['assignment_id', 'section', 'section_info', 'course', 'course_name',
                  'title', 'type', 'description', 'total_points', 'due_date',
                  'created_date', 'status', 'is_overdue']
        read_only_fields = ['assignment_id', 'created_date']

    def get_section_info(self, obj):
        return str(obj.section)


class SubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    assignment_points = serializers.IntegerField(source='assignment.total_points', read_only=True)
    percentage_score = serializers.ReadOnlyField()
    letter_grade = serializers.ReadOnlyField()

    class Meta:
        model = Submission
        fields = ['submission_id', 'assignment', 'assignment_title', 'assignment_points',
                  'student', 'student_name', 'submission_date', 'content',
                  'points_earned', 'percentage_score', 'letter_grade',
                  'feedback', 'graded_date', 'status']
        read_only_fields = ['submission_id', 'graded_date']


class StudentSubmissionSerializer(serializers.ModelSerializer):
    """Detailed submission serializer for students"""
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    assignment_type = serializers.CharField(source='assignment.type', read_only=True)
    assignment_points = serializers.IntegerField(source='assignment.total_points', read_only=True)
    due_date = serializers.DateField(source='assignment.due_date', read_only=True)
    course_name = serializers.CharField(source='assignment.course.course_name', read_only=True)
    percentage_score = serializers.ReadOnlyField()
    letter_grade = serializers.ReadOnlyField()

    class Meta:
        model = Submission
        fields = ['submission_id', 'assignment', 'assignment_title', 'assignment_type',
                  'assignment_points', 'due_date', 'course_name', 'submission_date',
                  'content', 'points_earned', 'percentage_score', 'letter_grade',
                  'feedback', 'graded_date', 'status']
        read_only_fields = ['submission_id']
