"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', users_views.RegisterView.as_view(), name='register'),
    path('register/student/', users_views.StudentRegisterView.as_view(), name='register_student'),
    path('register/teacher/', users_views.TeacherRegisterView.as_view(), name='register_teacher'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password-reset.html',
                                              email_template_name='users/email/password_reset_email.html',
                                              subject_template_name='users/email/password_reset_subject.txt'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password-reset-done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password-reset-confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password-reset-complete.html'),
         name='password_reset_complete'),
    path('progress/', include('charts.urls')),
    path('', include('quizzes.urls')),
]
