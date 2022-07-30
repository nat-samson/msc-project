from django.test import TestCase
from django.urls import reverse

from charts.forms import DateFilterForm, StudentDateFilterForm
from users.models import User


class ProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
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

    def test_progress_includes_form(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        form = response.context.get('form')
        self.assertIsInstance(form, DateFilterForm)

    def test_progress_context_when_no_student_data(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        words_due = response.context.get('words_due_revision')
        words_memorised = response.context.get('words_memorised')
        streak = response.context.get('current_streak')
        self.assertEquals(words_due, 0)
        self.assertEquals(words_memorised, 0)
        self.assertEquals(streak, 0)

    def test_progress_context_when_no_students(self):
        # Remove any students in the database
        User.objects.filter(is_teacher=False).delete()

        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        words_due = response.context.get('words_due_revision')
        words_memorised = response.context.get('words_memorised')
        streak = response.context.get('current_streak')
        self.assertEquals(words_due, 0)
        self.assertEquals(words_memorised, 0)
        self.assertEquals(streak, 0)


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_student', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        cls.path = reverse('dashboard')

    def test_dashboard_view_status(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_dashboard_template_name(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'charts/dashboard.html')

    def test_dashboard_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_dashboard_not_accessible_to_students(self):
        # a student attempting to access dashboard should be prompted to log in again
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        expected = reverse('login') + "?next=" + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected)

    def test_dashboard_accessible_to_teachers(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_includes_forms(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        student_filter = response.context.get('student_filter')
        date_filter = response.context.get('date_filter')
        self.assertIsInstance(date_filter, DateFilterForm)
        self.assertIsInstance(student_filter, StudentDateFilterForm)

    def test_dashboard_context_when_no_students(self):
        # Remove any students in the database
        User.objects.filter(is_teacher=False).delete()

        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        live_topics = response.context.get('live_topics')
        live_words = response.context.get('live_words')
        students_registered = response.context.get('students_registered')
        self.assertEquals(live_topics, 0)
        self.assertEquals(live_words, 0)
        self.assertEquals(students_registered, 0)
