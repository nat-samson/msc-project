from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from users.models import User


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
    pass
    # add any fields relevant only to students


class TeacherRegistrationForm(CustomUserCreationForm):
    # add any fields relevant only to teachers
    # TODO: Mechanism for checking a key, so students can't register as teachers

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_teacher = True
        user.is_staff = True
        user.save()
        return user
