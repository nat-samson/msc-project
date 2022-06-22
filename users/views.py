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

    def get_context_data(self, **kwargs):
        # add student to the context
        context = super().get_context_data(**kwargs)
        context['student_or_teacher'] = 'student'
        return context

    def form_valid(self, form):
        user = form.save()
        return redirect('login')


class TeacherRegisterView(CreateView):
    pass
