from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # enrollments = models.ManyToManyField(Course, related_name='enrolled_students')
    # Todo: profile picture implementation

    class Meta:
        abstract = True


class StudentProfile(Profile):
    pass
    # student specific fields


class TeacherProfile(Profile):
    pass
    # teacher specific fields
