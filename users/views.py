from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView

from .forms import StudentRegistrationForm
from .models import User


class RegisterView(TemplateView):
    template_name = 'users/register.html'


class StudentRegisterView(CreateView):
    model = User
    form_class = StudentRegistrationForm
    template_name = 'users/register_form.html'


class TeacherRegisterView(CreateView):
    pass
