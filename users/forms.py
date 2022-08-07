from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from myproject.settings import SITE_CODE
from users.models import User


def validate_site_code(value):
    # ensures that the user registering as a teacher knows the correct site code for their institution
    if value != SITE_CODE:
        raise ValidationError('Invalid site code, please contact your administrator.', code='invalid')


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
    # any fields unique to students go here
    pass


class TeacherRegistrationForm(CustomUserCreationForm):
    # site code helps to prevent students from signing up as teachers
    site_code = forms.CharField(max_length=50, widget=forms.PasswordInput,
                                help_text='Please type in the site code for your institution.',
                                validators=[validate_site_code])

    @transaction.atomic
    def save(self):
        # assign the appropriate privileges to the newly created teacher account
        user = super().save(commit=False)
        user.is_teacher = True
        user.is_staff = True
        user.save()
        return user
