from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm

from myproject.settings import SITE_CODE
from users.models import User


def validate_site_code(value):
    """Ensures that the user registering as a teacher knows the correct site code for their institution."""
    if value != SITE_CODE:
        raise ValidationError('Invalid site code, please contact your administrator.', code='invalid')


class CustomUserCreationForm(UserCreationForm):
    """Custom form template for registering new users, based on the Custom User model defined in users.models."""
    # Add fields relevant to students and teachers that are in the Custom User model.
    email = forms.EmailField()
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)

    class Meta:
        abstract = True
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class StudentRegistrationForm(CustomUserCreationForm):
    """Custom form for registering users as students."""
    # any fields unique to students would go here. Currently, just using the custom template as is.
    pass


class TeacherRegistrationForm(CustomUserCreationForm):
    """Custom form for registering users as teachers."""
    # site code helps to prevent students from signing themselves up as teachers
    site_code = forms.CharField(max_length=50, widget=forms.PasswordInput,
                                help_text='Please type in the site code for your institution.',
                                validators=[validate_site_code])

    field_order = ['username', 'email', 'first_name', 'last_name', 'site_code', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        # assign the appropriate privileges to the newly created teacher account
        user = super().save(commit=False)
        user.is_teacher = True
        user.is_staff = True
        user.save()
        return user


class UserUpdateForm(ModelForm):
    """Form for updating the user's email, first name and last name."""
    email = forms.EmailField()
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
