from django.contrib import auth
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.auth.views import PasswordResetView
from django.core import mail
from django.test import TestCase
from django.urls import reverse, resolve

from .forms import StudentRegistrationForm, TeacherRegistrationForm
from .models import User
from .views import StudentRegisterView, TeacherRegisterView

# set up some common variables
good_user_input = {
            'username': 'testuser',
            'email': 'email@email.com',
            'first_name': 'test',
            'last_name': 'user',
            'password1': 'djangotest123',
            'password2': 'djangotest123'
        }


class StudentRegisterTests(TestCase):
    def setUp(self):
        url = reverse('register_student')
        self.response = self.client.get(url)

        # test successful registration
        self.response_post = self.client.post(url, good_user_input)

    def test_register_view_status(self):
        self.assertEquals(200, self.response.status_code)

    def test_register_view_url(self):
        view = resolve('/register/student/')
        self.assertIs(view.func.view_class, StudentRegisterView)

    def test_register_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, StudentRegistrationForm)

    def test_register_form_fields(self):
        # this tests the form directly (and field order), not the form as part of a rendered view
        form = StudentRegistrationForm()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        self.assertSequenceEqual(fields, tuple(form.fields))

    def test_form_has_intended_inputs(self):
        # form must have exactly these inputs:
        # CSRF token, username, email, firstname, lastname, password, confirm-password
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

        # form must have no extra inputs beyond those specified above
        self.assertContains(self.response, '<input type=', 7)

    def test_user_registration(self):
        self.assertTrue(User.objects.exists())
        self.assertEquals('testuser', User.objects.get(pk=1).username)


class UnsuccessfulStudentRegisterTests(TestCase):
    def setUp(self):
        # simulates user submitting form with no data
        url = reverse('register_student')
        self.response = self.client.post(url, {})

    def test_signup_fail_status(self):
        self.assertEquals(200, self.response.status_code)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_user_fail_registration(self):
        self.assertFalse(User.objects.exists())


class TeacherRegisterTests(TestCase):
    def setUp(self):
        url = reverse('register_teacher')
        self.response = self.client.get(url)

        # Teacher instances expect existence of Group
        Group.objects.create(name='Teachers')

        # test successful registration
        self.response_post = self.client.post(url, good_user_input)

    def test_register_view_status(self):
        self.assertEquals(200, self.response.status_code)

    def test_register_view_url(self):
        view = resolve('/register/teacher/')
        self.assertIs(view.func.view_class, TeacherRegisterView)

    def test_register_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, TeacherRegistrationForm)

    def test_register_form_fields(self):
        # this tests the form directly (and field order), not the form as part of a rendered view
        form = TeacherRegistrationForm()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        self.assertSequenceEqual(fields, tuple(form.fields))

    def test_form_has_intended_inputs(self):
        # form must have exactly these inputs:
        # CSRF token, username, email, firstname, lastname, password, confirm-password
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

        # form must have no extra inputs beyond those specified above
        self.assertContains(self.response, '<input type=', 7)

    def test_user_registration(self):
        self.assertTrue(User.objects.exists())
        self.assertEquals('testuser', User.objects.get(pk=1).username)


class UnsuccessfulTeacherRegisterTests(TestCase):
    def setUp(self):
        # simulates user submitting form with no data
        url = reverse('register_teacher')
        self.response = self.client.post(url, {})

    def test_signup_fail_status(self):
        self.assertEquals(200, self.response.status_code)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_user_fail_registration(self):
        self.assertFalse(User.objects.exists())


class LoginTests(TestCase):
    def setUp(self):
        # create a test user
        self.credentials = {'username': 'testuser', 'password': 'testuser1234', 'email': 'email@email.com'}
        self.user = User.objects.create_user(**self.credentials)
        self.url = reverse('login')
        self.login_input = {
            'username': 'testuser',
            'password': 'testuser1234'
        }

    def test_successful_login(self):
        self.response = self.client.post(self.url, self.login_input)
        self.assertIn('_auth_user_id', self.client.session)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_wrong_username(self):
        self.login_input['username'] = 'wrongusername'
        self.response = self.client.post(self.url, self.login_input)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_login_wrong_password(self):
        self.login_input['password'] = 'wrongpassword'
        self.response = self.client.post(self.url, self.login_input)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout(self):
        # first, log testuser in
        self.response = self.client.post(self.url, self.login_input)

        # now log testuser out
        self.response = self.client.get(reverse('logout'))
        user = auth.get_user(self.client)

        # testuser is no longer authenticated, and the active user in the client is now AnonymousUser instance
        self.assertFalse(user.is_authenticated)
        self.assertEqual(user, AnonymousUser())


class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.get(url)

    def test_password_reset_view_status(self):
        self.assertEquals(self.response.status_code, 200)

    def test_password_reset_view_url(self):
        view = resolve('/password-reset/')
        self.assertEquals(PasswordResetView, view.func.view_class)

    def test_form_has_intended_inputs(self):
        # form must have exactly these inputs: CSRF token, email
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        self.assertContains(self.response, 'type="email"', 1)

        # form must have no extra inputs beyond those specified above
        self.assertContains(self.response, '<input type=', 2)


class PasswordResetValidUserTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', email='email@email.com', password='testuser1234',
                                 first_name='test', last_name='user')
        self.url = reverse('password_reset')
        self.response = self.client.post(self.url, {'email': 'email@email.com'})

    def test_password_reset_redirect(self):
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self):
        self.assertEqual(1, len(mail.outbox))


class PasswordResetInvalidUserTests(TestCase):
    def setUp(self):
        self.url = reverse('password_reset')
        self.response = self.client.post(self.url, {'email': 'notregistered@email.com'})

    def test_password_reset_nonexistent_user(self):
        # nb page still redirects even if email not recognised in database (prevents info leaking of registered emails)
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self):
        # page redirects, but no email actually gets sent
        self.assertEqual(0, len(mail.outbox))
