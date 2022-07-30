from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    streak = models.PositiveIntegerField(default=0)

    REQUIRED_FIELDS = ['is_teacher']

    def __str__(self):
        if self.is_superuser:
            role = "Admin"
        elif self.is_teacher:
            role = "Teacher"
        else:
            role = "Student"
        return f'{self.first_name} {self.last_name} ({role})'
