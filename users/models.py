from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # fields common to both students and teachers go here
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    # courses = models.ManyToManyField(Course, related_name='courses')

    def __str__(self):
        if self.is_superuser:
            role = "Admin"
        else:
            role = "Teacher" if self.is_teacher else "Student"
        return f'{self.first_name} {self.last_name} ({role})'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Todo: profile picture implementation

    class Meta:
        abstract = True


class StudentProfile(Profile):
    pass
    # student specific fields


class TeacherProfile(Profile):
    pass
    # teacher specific fields
