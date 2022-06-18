from django.contrib.auth.models import User
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
