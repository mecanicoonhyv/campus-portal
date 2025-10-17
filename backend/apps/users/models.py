from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_faculty(self):
        return self.role == 'faculty'

    @property
    def is_staff_member(self):
        return self.role == 'staff'


class StudentProfile(models.Model):
    """Extended profile for students"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Graduated', 'Graduated'),
        ('Suspended', 'Suspended'),
    ]

    YEAR_CHOICES = [
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
        ('Graduate', 'Graduate'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    major = models.CharField(max_length=100)
    year_level = models.CharField(max_length=20, choices=YEAR_CHOICES)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    emergency_contact = models.CharField(max_length=200)
    emergency_phone = models.CharField(max_length=20)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


class FacultyProfile(models.Model):
    """Extended profile for faculty and professors"""
    RANK_CHOICES = [
        ('Full Professor', 'Full Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Professor Emeritus', 'Professor Emeritus'),
        ('Visiting Professor', 'Visiting Professor'),
        ('Clinical Professor', 'Clinical Professor'),
        ('Lecturer', 'Lecturer'),
        ('Instructor', 'Instructor'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Retired', 'Retired'),
        ('On Leave', 'On Leave'),
    ]

    EDUCATION_CHOICES = [
        ('PhD', 'PhD'),
        ('EdD', 'EdD'),
        ('Masters', 'Masters'),
        ('Bachelors', 'Bachelors'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    rank = models.CharField(max_length=50, choices=RANK_CHOICES)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    office_building = models.CharField(max_length=100, blank=True)
    office_number = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    years_experience = models.IntegerField(default=0)
    research_areas = models.TextField(blank=True)
    publications = models.IntegerField(default=0)
    is_professor = models.BooleanField(default=False)

    class Meta:
        ordering = ['faculty_id']
        verbose_name_plural = 'Faculty profiles'

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"


class StaffProfile(models.Model):
    """Extended profile for administrative staff"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    office_building = models.CharField(max_length=100, blank=True)
    office_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['staff_id']
        verbose_name_plural = 'Staff profiles'

    def __str__(self):
        return f"{self.staff_id} - {self.user.get_full_name()}"
