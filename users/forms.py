from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from users.models import User, StudentProfile


# add email as an additional field to the register form
class CustomUserCreationForm(UserCreationForm):
    # add fields relevant to students and teachers that are in the Custom User model
    email = forms.EmailField()
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)

    class Meta:
        abstract = True
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class StudentRegistrationForm(CustomUserCreationForm):
    # add fields relevant only to students

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()

        # auto-create the connected student profile
        student = StudentProfile.objects.create(user=user)

        # here's where you'd add extra info to the student profile

        return user


class TeacherRegistrationForm(CustomUserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
