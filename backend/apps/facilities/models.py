from django.db import models


class Building(models.Model):
    """Campus buildings"""
    building_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    capacity = models.IntegerField(default=0)
    floors = models.IntegerField(default=1)
    year_built = models.IntegerField(null=True, blank=True)
    facilities = models.TextField(blank=True, help_text="Comma-separated list of facilities")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    """Individual rooms within buildings"""
    ROOM_TYPE_CHOICES = [
        ('Classroom', 'Classroom'),
        ('Lecture Hall', 'Lecture Hall'),
        ('Laboratory', 'Laboratory'),
        ('Office', 'Office'),
        ('Conference', 'Conference'),
        ('Other', 'Other'),
    ]

    room_id = models.CharField(max_length=20, unique=True, primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES, default='Classroom')
    capacity = models.IntegerField(default=30)
    equipment = models.TextField(blank=True, help_text="Comma-separated list of equipment")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['building', 'room_number']

    def __str__(self):
        return f"{self.building.name} {self.room_number}"
