from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from charts.chart_tools import unzip
from users.models import User


class ProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234', is_student=True)
        cls.path = reverse('progress')

    def test_progress_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_progress_template_name(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'charts/progress.html')

    def test_progress_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234', is_student=True)
        cls.path = reverse('dashboard')

    def test_dashboard_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_dashboard_template_name(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'charts/dashboard.html')

    def test_dashboard_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class ChartTools(SimpleTestCase):
    def test_unzip(self):
        zipped_data = [(1, "a"), (2, "b"), (3, "c")]
        expected = [(1, 2, 3), ("a", "b", "c")]
        actual = unzip(zipped_data)
        self.assertEquals(expected, actual)
