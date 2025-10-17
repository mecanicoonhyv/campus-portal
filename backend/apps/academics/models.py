from django.db import models
from apps.users.models import User, StudentProfile, FacultyProfile
from apps.facilities.models import Room


class Department(models.Model):
    """Academic departments"""
    department_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    head = models.CharField(max_length=200, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    building = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    """Course catalog"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    LEVEL_CHOICES = [
        ('Undergraduate', 'Undergraduate'),
        ('Graduate', 'Graduate'),
    ]

    course_id = models.CharField(max_length=20, unique=True, primary_key=True)
    course_name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='courses')
    credits = models.IntegerField(default=3)
    description = models.TextField()
    prerequisites = models.CharField(max_length=200, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['course_id']

    def __str__(self):
        return f"{self.course_id} - {self.course_name}"


class Section(models.Model):
    """Course sections/classes"""
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Cancelled', 'Cancelled'),
    ]

    SEMESTER_CHOICES = [
        ('Fall 2024', 'Fall 2024'),
        ('Spring 2025', 'Spring 2025'),
        ('Summer 2024', 'Summer 2024'),
        ('Fall 2025', 'Fall 2025'),
    ]

    section_id = models.CharField(max_length=20, unique=True, primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    section_number = models.CharField(max_length=10)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    year = models.IntegerField()
    instructor = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, related_name='sections_teaching')
    instructor_name = models.CharField(max_length=200)
    instructor_rank = models.CharField(max_length=50)
    meeting_days = models.CharField(max_length=20)
    meeting_time = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    capacity = models.IntegerField(default=30)
    enrolled = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    class Meta:
        ordering = ['semester', 'course']

    def __str__(self):
        return f"{self.course.course_id} - {self.section_number} ({self.semester})"

    @property
    def is_full(self):
        return self.enrolled >= self.capacity

    @property
    def available_seats(self):
        return self.capacity - self.enrolled


class Enrollment(models.Model):
    """Student enrollments in course sections"""
    STATUS_CHOICES = [
        ('Enrolled', 'Enrolled'),
        ('Withdrawn', 'Withdrawn'),
        ('Completed', 'Completed'),
    ]

    GRADE_CHOICES = [
        ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D+', 'D+'), ('D', 'D'), ('D-', 'D-'),
        ('F', 'F'),
        ('W', 'W'), ('I', 'I'), ('P', 'P'),
    ]

    GRADE_POINTS = {
        'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0, 'W': 0.0, 'I': 0.0, 'P': 0.0,
    }

    enrollment_id = models.CharField(max_length=20, unique=True, primary_key=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    student_name = models.CharField(max_length=200)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.CharField(max_length=20)
    enrollment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Enrolled')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    credits_attempted = models.IntegerField(default=0)
    credits_earned = models.IntegerField(default=0)

    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ['student', 'section']

    def __str__(self):
        return f"{self.student.student_id} - {self.section}"

    def save(self, *args, **kwargs):
        if self.grade and self.grade in self.GRADE_POINTS:
            self.grade_points = self.GRADE_POINTS[self.grade]
            if self.grade not in ['F', 'W', 'I']:
                self.credits_earned = self.course.credits
        super().save(*args, **kwargs)
