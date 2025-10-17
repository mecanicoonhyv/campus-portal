from django.db import models
from apps.academics.models import Section, Course
from apps.users.models import StudentProfile


class Assignment(models.Model):
    """Course assignments"""
    TYPE_CHOICES = [
        ('Homework', 'Homework'),
        ('Quiz', 'Quiz'),
        ('Midterm', 'Midterm'),
        ('Final', 'Final'),
        ('Project', 'Project'),
        ('Essay', 'Essay'),
        ('Lab', 'Lab'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Active', 'Active'),
        ('Closed', 'Closed'),
        ('Graded', 'Graded'),
    ]

    assignment_id = models.CharField(max_length=20, unique=True, primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    total_points = models.IntegerField(default=100)
    due_date = models.DateField()
    created_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.course_id} - {self.title}"

    @property
    def is_overdue(self):
        from datetime import date
        return date.today() > self.due_date if self.status == 'Active' else False


class Submission(models.Model):
    """Student assignment submissions"""
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Late', 'Late'),
        ('Graded', 'Graded'),
        ('Missing', 'Missing'),
    ]

    submission_id = models.CharField(max_length=20, unique=True, primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    student_name = models.CharField(max_length=200)
    submission_date = models.DateTimeField(null=True, blank=True)
    content = models.TextField(blank=True, help_text="Submission content or file reference")
    points_earned = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Submitted')

    class Meta:
        ordering = ['-submission_date']
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title}"

    @property
    def percentage_score(self):
        if self.points_earned and self.assignment.total_points:
            return (self.points_earned / self.assignment.total_points) * 100
        return None

    @property
    def letter_grade(self):
        score = self.percentage_score
        if score is None:
            return None
        if score >= 93: return 'A'
        if score >= 90: return 'A-'
        if score >= 87: return 'B+'
        if score >= 83: return 'B'
        if score >= 80: return 'B-'
        if score >= 77: return 'C+'
        if score >= 73: return 'C'
        if score >= 70: return 'C-'
        if score >= 67: return 'D+'
        if score >= 63: return 'D'
        if score >= 60: return 'D-'
        return 'F'
