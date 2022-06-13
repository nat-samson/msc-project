from django.test import TestCase
from django.urls import reverse


class HomeTests(TestCase):
    def test_home_view_status(self):
        url = reverse('home')
        self.assertEquals(self.client.get(url).status_code, 200)
