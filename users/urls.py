from django.contrib.auth import views as auth_views
from django.urls import path

from users import views as users_views

urlpatterns = [
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
    path('profile/', users_views.UserUpdateView.as_view(), name='profile'),
    path('password/', users_views.CustomPasswordChangeView.as_view(), name='password_change'),
]
