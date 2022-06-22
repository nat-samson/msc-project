from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView

from .forms import StudentRegistrationForm, TeacherRegistrationForm
from .models import User


class RegisterView(TemplateView):
    template_name = 'users/register.html'


class StudentRegisterView(CreateView):
    form_class = StudentRegistrationForm
    template_name = 'users/register_form.html'

    def get_context_data(self, **kwargs):
        # add student to the context
        context = super().get_context_data(**kwargs)
        context['student_or_teacher'] = 'student'
        return context

    def form_valid(self, form):
        # validate the form, log the user in and send them to homepage
        user = form.save()
        login(self.request, user)
        return redirect('home')


class TeacherRegisterView(CreateView):
    form_class = TeacherRegistrationForm
    template_name = 'users/register_form.html'

    def get_context_data(self, **kwargs):
        # add student to the context
        context = super().get_context_data(**kwargs)
        context['student_or_teacher'] = 'teacher'
        return context

    def form_valid(self, form):
        user = form.save()

        # grant Teacher-level permissions in Admin
        teacher_group = Group.objects.get(name='Teachers')
        user.groups.add(teacher_group)

        login(self.request, user)
        return redirect('home')
