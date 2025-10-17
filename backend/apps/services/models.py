from django.db import models
from apps.users.models import StudentProfile


class FinancialAid(models.Model):
    """Student financial aid awards"""
    TYPE_CHOICES = [
        ('Grant', 'Grant'),
        ('Scholarship', 'Scholarship'),
        ('Loan', 'Loan'),
        ('Work Study', 'Work Study'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Disbursed', 'Disbursed'),
        ('Rejected', 'Rejected'),
    ]

    aid_id = models.CharField(max_length=20, unique=True, primary_key=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='financial_aid')
    student_name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200, help_text="Name of grant/scholarship/loan")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    disbursement_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-disbursement_date']
        verbose_name_plural = 'Financial aid'

    def __str__(self):
        return f"{self.student.student_id} - {self.name}"


class ParkingPermit(models.Model):
    """Student parking permits"""
    PERMIT_TYPE_CHOICES = [
        ('Student', 'Student'),
        ('Faculty', 'Faculty'),
        ('Staff', 'Staff'),
        ('Visitor', 'Visitor'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Suspended', 'Suspended'),
        ('Cancelled', 'Cancelled'),
    ]

    permit_id = models.CharField(max_length=20, unique=True, primary_key=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='parking_permits')
    student_name = models.CharField(max_length=200)
    permit_type = models.CharField(max_length=20, choices=PERMIT_TYPE_CHOICES, default='Student')
    lot_number = models.CharField(max_length=20)
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.IntegerField()
    license_plate = models.CharField(max_length=20)
    issue_date = models.DateField()
    expiration_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.permit_id} - {self.student.student_id}"

    @property
    def is_expired(self):
        from datetime import date
        return date.today() > self.expiration_date


class Event(models.Model):
    """Campus events"""
    TYPE_CHOICES = [
        ('Academic', 'Academic'),
        ('Social', 'Social'),
        ('Sports', 'Sports'),
        ('Cultural', 'Cultural'),
        ('Workshop', 'Workshop'),
        ('Meeting', 'Meeting'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    event_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200)
    capacity = models.IntegerField(default=0)
    registered = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} - {self.date}"

    @property
    def is_full(self):
        return self.registered >= self.capacity if self.capacity > 0 else False

    @property
    def available_spots(self):
        return max(0, self.capacity - self.registered) if self.capacity > 0 else None
