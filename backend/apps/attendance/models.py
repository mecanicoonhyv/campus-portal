from django.db import models
from apps.users.models import StudentProfile
from apps.academics.models import Section


class AttendanceRecord(models.Model):
    """Class attendance tracking"""
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    ]

    record_id = models.CharField(max_length=20, unique=True, primary_key=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    student_name = models.CharField(max_length=200)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='attendance_records')
    course_id = models.CharField(max_length=20)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['student', 'section', 'date']

    def __str__(self):
        return f"{self.student.student_id} - {self.section} - {self.date}"
