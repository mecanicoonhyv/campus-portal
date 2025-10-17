from django.db import models
from apps.users.models import StudentProfile


class Book(models.Model):
    """Library book catalog"""
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Checked Out', 'Checked Out'),
        ('Reserved', 'Reserved'),
        ('Lost', 'Lost'),
        ('Damaged', 'Damaged'),
    ]

    book_id = models.CharField(max_length=20, unique=True, primary_key=True)
    isbn = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100, help_text="Shelf location")
    copies_total = models.IntegerField(default=1)
    copies_available = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.book_id} - {self.title}"


class Checkout(models.Model):
    """Library book checkouts"""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
        ('Lost', 'Lost'),
    ]

    checkout_id = models.CharField(max_length=20, unique=True, primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='checkouts')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='library_checkouts')
    student_name = models.CharField(max_length=200)
    checkout_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-checkout_date']

    def __str__(self):
        return f"{self.student.student_id} - {self.book.title}"

    @property
    def is_overdue(self):
        from datetime import date
        if self.status == 'Active' and self.due_date < date.today():
            return True
        return False

    @property
    def days_overdue(self):
        from datetime import date
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0
