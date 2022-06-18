from django.test import TestCase
from django.urls import reverse, resolve
from .views import register


class RegisterTests(TestCase):
    def test_register_vew_status(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)

    def test_register_view_url(self):
        view = resolve('/register/')
        self.assertEquals(view.func, register)
