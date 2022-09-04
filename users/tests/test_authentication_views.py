from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import PasswordResetView
from django.core import mail
from django.test import TestCase
from django.urls import reverse, resolve

from users.models import User

# set up some common variables
good_user_input = {
            'username': 'test_user',
            'email': 'email@email.com',
            'first_name': 'test',
            'last_name': 'user',
            'password1': 'djangotest123',
            'password2': 'djangotest123'
        }


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create a test user
        credentials = {'username': 'test_user', 'password': 'test_user1234', 'email': 'email@email.com'}
        cls.test_user = User.objects.create_user(**credentials)
        cls.url = reverse('login')
        cls.login_input = {
            'username': 'test_user',
            'password': 'test_user1234'
        }

    def test_successful_login(self):
        self.client.post(self.url, self.login_input)
        user = auth.get_user(self.client)

        self.assertIn('_auth_user_id', self.client.session)
        self.assertTrue(user.is_authenticated)
        self.assertEquals(user, self.test_user)

    def test_login_wrong_username(self):
        bad_login_input = {
            'username': 'wrong',
            'password': 'test_user1234'
        }
        self.client.post(self.url, bad_login_input)
        user = auth.get_user(self.client)

        self.assertFalse(user.is_authenticated)

    def test_login_wrong_password(self):
        bad_login_input = {
            'username': 'test_user',
            'password': 'wrong'
        }
        self.client.post(self.url, bad_login_input)
        user = auth.get_user(self.client)

        self.assertFalse(user.is_authenticated)

    def test_logout(self):
        # log test_user in and then out
        self.client.force_login(self.test_user)
        self.client.get(reverse('logout'))

        # active user in the client is now AnonymousUser instance
        active_user = auth.get_user(self.client)
        self.assertFalse(active_user.is_authenticated)
        self.assertEqual(active_user, AnonymousUser())


class PasswordResetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('password_reset')

    def test_password_reset_view_status(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_password_reset_view_url(self):
        view = resolve('/u/password-reset/')
        self.assertEquals(PasswordResetView, view.func.view_class)

    def test_form_has_intended_inputs(self):
        # form must have exactly these inputs: CSRF token, email
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'type="email"', 1)

        # form must have no extra inputs beyond those specified above
        self.assertContains(response, '<input type=', 2)


class PasswordResetValidUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='test_user', email='email@email.com', password='test_user1234')
        cls.url = reverse('password_reset')

    def test_password_reset_redirect(self):
        response = self.client.post(self.url, {'email': 'email@email.com'})
        url = reverse('password_reset_done')
        self.assertRedirects(response, url)

    def test_send_password_reset_email(self):
        self.client.post(self.url, {'email': 'email@email.com'})
        self.assertEqual(1, len(mail.outbox))


class PasswordResetInvalidUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('password_reset')

    def test_password_reset_nonexistent_email(self):
        # page still redirects even if email not recognised in database to prevent info leaks
        response = self.client.post(self.url, {'email': 'notregistered@email.com'})
        url = reverse('password_reset_done')
        self.assertRedirects(response, url)

    def test_send_password_reset_email(self):
        # page redirects, but no email actually gets sent
        self.assertEqual(0, len(mail.outbox))
