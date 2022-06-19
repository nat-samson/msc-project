from django.contrib import auth
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from django.urls import reverse, resolve

from quizzes.forms import UserRegistrationForm
from .views import register


class RegisterTests(TestCase):
    def setUp(self):
        url = reverse('register')
        self.response = self.client.get(url)

        # test successful registration
        user_input = {
            'username': 'nathaniel',
            'email': 'email@email.com',
            'password1': 'djangotest123',
            'password2': 'djangotest123'
        }
        self.response_post = self.client.post(url, user_input)

    def test_register_vew_status(self):
        self.assertEquals(200, self.response.status_code)

    def test_register_view_url(self):
        view = resolve('/register/')
        self.assertEquals(register, view.func)

    def test_register_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, UserRegistrationForm)

    def test_register_form_fields(self):
        # this tests the form directly, not the form as part of a rendered view
        form = UserRegistrationForm()
        fields = ('username', 'email', 'password1', 'password2')
        self.assertSequenceEqual(fields, tuple(form.fields))

    def test_form_has_intended_inputs(self):
        # form must have exactly these inputs: CSRF token, username, email, password, confirm-password
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

        # form must have no extra inputs beyond those specified above
        self.assertContains(self.response, '<input type=', 5)

    def test_user_registration(self):
        self.assertTrue(User.objects.exists())
        self.assertEquals('nathaniel', User.objects.get(pk=1).username)


class UnsuccessfulRegisterTests(TestCase):
    def setUp(self):
        # simulates user submitting form with no data
        user_input = {}
        url = reverse('register')
        self.response = self.client.post(url, user_input)

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
        self.user_input = {
            'username': 'testuser',
            'password': 'testuser1234'
        }

    def test_successful_login(self):
        self.response = self.client.post(self.url, self.user_input)
        self.assertIn('_auth_user_id', self.client.session)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_unsuccessful_login(self):
        self.user_input['password'] = 'wrongpassword'
        self.response = self.client.post(self.url, self.user_input)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout(self):
        # first, log testuser in
        self.response = self.client.post(self.url, self.user_input)

        # now log testuser out
        self.response = self.client.get(reverse('logout'))
        user = auth.get_user(self.client)

        # testuser is no longer authenticated, and the active user in the client is now AnonymousUser instance
        self.assertFalse(user.is_authenticated)
        self.assertEqual(user, AnonymousUser())
