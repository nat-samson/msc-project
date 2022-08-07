import copy

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse, resolve

from myproject.settings import SITE_CODE
from users.forms import StudentRegistrationForm, TeacherRegistrationForm
from users.models import User
from users.views import RegisterView, StudentRegisterView, TeacherRegisterView

# set up some common variables
good_user_input = {
            'username': 'test_user',
            'email': 'email@email.com',
            'first_name': 'test',
            'last_name': 'user',
            'password1': 'djangotest123',
            'password2': 'djangotest123',
            'site_code': SITE_CODE,
        }


class RegisterLandingPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('register')

    def test_register_view_status(self):
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)

    def test_register_view_url(self):
        view = resolve('/register/')
        self.assertIs(view.func.view_class, RegisterView)


class StudentRegisterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('register_student')

    def test_register_view_status(self):
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)

    def test_register_view_url(self):
        view = resolve('/register/student/')
        self.assertIs(view.func.view_class, StudentRegisterView)

    def test_register_form(self):
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, StudentRegistrationForm)

    def test_register_form_fields(self):
        # this tests the form directly (and field order), not the form as part of a rendered view
        form = StudentRegistrationForm()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        self.assertSequenceEqual(fields, tuple(form.fields))

    def test_form_has_intended_inputs(self):
        # form must have exactly these inputs:
        # CSRF token, username, email, firstname, lastname, password, confirm-password
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'type="text"', 3)
        self.assertContains(response, 'type="email"', 1)
        self.assertContains(response, 'type="password"', 2)

        # form must have no extra inputs beyond those specified above
        self.assertContains(response, '<input type=', 7)

    def test_user_registration(self):
        # test successful registration
        self.client.post(self.url, good_user_input)
        self.assertTrue(User.objects.exists())
        self.assertEquals('test_user', User.objects.get(pk=1).username)


class UnsuccessfulStudentRegisterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # simulate user submitting form with no data
        cls.url = reverse('register_student')

    def test_signup_fail_status(self):
        response = self.client.post(self.url, {})
        self.assertEquals(200, response.status_code)

    def test_form_errors(self):
        response = self.client.post(self.url, {})
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_user_fail_registration(self):
        self.assertFalse(User.objects.exists())


class TeacherRegisterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Teacher instances expect existence of Group
        Group.objects.create(name='Teachers')
        cls.url = reverse('register_teacher')

    def test_register_view_status(self):
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)

    def test_register_view_url(self):
        view = resolve('/register/teacher/')
        self.assertIs(view.func.view_class, TeacherRegisterView)

    def test_register_form(self):
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, TeacherRegistrationForm)

    def test_register_form_fields(self):
        # this tests the form directly (and field order), not the form as part of a rendered view
        form = TeacherRegistrationForm()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'site_code')
        self.assertSequenceEqual(fields, tuple(form.fields))

    def test_form_has_intended_inputs(self):
        # form must have exactly these inputs:
        # CSRF token, username, email, firstname, lastname, password, confirm-password
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken', 1)
        self.assertContains(response, 'type="text"', 3)
        self.assertContains(response, 'type="email"', 1)
        self.assertContains(response, 'type="password"', 3)

        # form must have no extra inputs beyond those specified above
        self.assertContains(response, '<input type=', 8)

    def test_user_registration(self):
        # test successful registration
        self.client.post(self.url, good_user_input)
        self.assertTrue(User.objects.exists())
        self.assertEquals('test_user', User.objects.get(pk=1).username)


class UnsuccessfulTeacherRegisterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # simulates user submitting form with no data
        cls.url = reverse('register_teacher')

    def test_signup_fail_status(self):
        response = self.client.post(self.url, {})
        self.assertEquals(200, response.status_code)

    def test_form_errors(self):
        response = self.client.post(self.url, {})
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_site_code_required(self):
        bad_input = copy.deepcopy(good_user_input)
        bad_input['site_code'] = "invalid-site-code!!!"
        response = self.client.post(self.url, bad_input)
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_user_fail_registration(self):
        self.assertFalse(User.objects.exists())
