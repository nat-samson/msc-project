from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# add email as an additional field to the register form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
