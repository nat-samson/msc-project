from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import StudentRegistrationForm, TeacherRegistrationForm, UserUpdateForm


class RegisterView(TemplateView):
    """View for registration landing page - letting a user indicate if they are a student or teacher."""
    template_name = 'users/register.html'


class CreateUserView(CreateView):
    """Base view that processes the actual registration of a new user."""
    template_name = 'users/register_form.html'

    def form_valid(self, form):
        # validate the form, log the user in and send them to homepage
        user = form.save()
        login(self.request, user)
        return redirect('home')


class StudentRegisterView(CreateUserView):
    """Student version of the CreateUserView."""
    form_class = StudentRegistrationForm


class TeacherRegisterView(CreateUserView):
    """Teacher version of the CreateUserView."""
    form_class = TeacherRegistrationForm


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a user's details according to the UserUpdateForm."""
    form_class = UserUpdateForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)


class CustomPasswordChangeView(PasswordChangeView):
    """View for updating a user's password."""
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Password updated successfully!")
        return super().form_valid(form)
