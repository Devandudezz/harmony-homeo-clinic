from django.db import models
from django.utils import timezone

class Patient(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)  # Not mandatory
    email = models.EmailField(blank=True)  # Not mandatory
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(null=True, blank=True)  # Manually editable
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name
