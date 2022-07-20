from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from charts import chart_tools
from charts.chart_tools import unzip, get_colours
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
    def test_unzip_good_input(self):
        zipped_data = [(1, "a"), (2, "b"), (3, "c")]
        expected = [(1, 2, 3), ("a", "b", "c")]
        actual = unzip(zipped_data)
        self.assertEquals(expected, actual)

    def test_unzip_single_tuple(self):
        zipped_data = [(1, "a")]
        expected = [(1,), ("a",)]
        actual = unzip(zipped_data)
        self.assertEquals(expected, actual)

    def test_unzip_empty(self):
        empty_zip = []
        expected = []
        actual = unzip(empty_zip)
        self.assertEquals(expected, actual)

    def test_get_zero_colours(self):
        expected = []
        actual = get_colours(0)
        self.assertEquals(expected, actual)

    def test_cycle_through_colours(self):
        # get more colours than there are presets
        n = len(chart_tools.DEFAULT_CHART_PALETTE)
        colours = get_colours(5 * n)

        # the nth colour should be identical to the 2*nth, 3*nth etc.
        n_colour = colours[0][n]
        n2_colour = colours[0][n * 2]
        n3_colour = colours[0][n * 3]
        n_plus_1_colour = colours[0][n + 1]
        n2_plus_1_colour = colours[0][2 * n + 1]
        self.assertEquals(n_colour, n2_colour)
        self.assertEquals(n_colour, n3_colour)
        self.assertEquals(n_plus_1_colour, n2_plus_1_colour)

    def test_get_colours_when_no_presets(self):
        empty_preset_palette = []
        actual = get_colours(5, empty_preset_palette)
        expected = []
        self.assertEquals(expected, actual)
