from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve
from .views import register


class RegisterTests(TestCase):
    def setUp(self):
        url = reverse('register')
        self.response = self.client.get(url)

        # test successful registration
        user_input = {
            'username': 'nathaniel',
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
        self.assertIsInstance(form, UserCreationForm)

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
