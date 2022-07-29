import datetime
import json

from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from charts import chart_tools
from charts.chart_data import PTS_PER_DAY_DATERANGE
from charts.chart_tools import unzip, get_colours
from charts.forms import DateFilterForm, StudentDateFilterForm
from quizzes.models import QuizResults, Topic
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


class FilteredStudentDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        cls.path = reverse('filter-date-student')

    def test_filtered_student_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_filtered_student_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_filtered_student_json_no_data(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {"points_earned": 0, "quizzes_taken": 0, "correct_pc": "N/A"}
        self.assertJSONEqual(actual, expected)

    def test_filtered_student_when_no_students(self):
        # Remove any students in the database
        User.objects.filter(is_teacher=False).delete()

        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {"points_earned": 0, "quizzes_taken": 0, "correct_pc": "N/A"}
        self.assertJSONEqual(actual, expected)


class FilteredTeacherDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_student', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        cls.path = reverse('filter-date-teacher')

    def test_filtered_teacher_view_status(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_filtered_teacher_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_filtered_teacher_not_accessible_to_students(self):
        # a student attempting to access dashboard should be prompted to log in again
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        expected = reverse('login') + "?next=" + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected)

    def test_filtered_teacher_accessible_to_teachers(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_filtered_teacher_json_no_students(self):
        # Remove any students in the database
        User.objects.filter(is_teacher=False).delete()

        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {"active_students": 0, "quizzes_taken": 0, "points_earned": 0}
        self.assertJSONEqual(actual, expected)


class FilteredDataDateTopicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_student', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        cls.path = reverse('filter-date-topic')

    def test_filtered_date_topic_view_status(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_filtered_date_topic_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_filtered_date_topic_not_accessible_to_students(self):
        # a student attempting to access dashboard should be prompted to log in again
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        expected = reverse('login') + "?next=" + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected)

    def test_filtered_date_topic_accessible_to_teachers(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_filtered_date_topic_json_no_students(self):
        # Remove any students in the database
        User.objects.filter(is_teacher=False).delete()

        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = [["No Students Registered!", "N/A"]]
        self.assertJSONEqual(actual, expected)


class UpdatableChartsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_student', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        cls.path = reverse('data-updatable-charts')

    def test_updatable_charts_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_updatable_charts_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_updatable_charts_from_teacher_with_data(self):
        # Add a Quiz Result to the database
        today = datetime.date.today()
        self.animals = Topic.objects.create(name='Animals')
        QuizResults.objects.create(student=self.student, correct_answers=10, incorrect_answers=5,
                                   date_created=today, topic=self.animals, points=100)

        filter_string = "?student=1&date_to=" + str(today)
        filter_url = self.path + filter_string

        self.client.force_login(self.teacher)
        response = self.client.get(filter_url)
        response_dict = json.loads(response.content)

        # among the colour data etc. ensure that the correct database values have been retrieved
        self.assertEquals(response_dict['points_per_topic']['labels'], ['Animals'])
        self.assertEquals(response_dict['points_per_topic']['datasets'][0]['data'], [100])
        self.assertEquals(response_dict['quizzes_per_topic']['labels'], ['Animals'])
        self.assertEquals(response_dict['quizzes_per_topic']['datasets'][0]['data'], [1])

    def test_updatable_charts_from_student_no_data(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {'points_per_topic': [], 'quizzes_per_topic': []}
        self.assertJSONEqual(actual, expected)

    def test_updatable_charts_from_teacher_no_students(self):
        # Remove any students in the database
        User.objects.filter(is_teacher=False).delete()

        # teacher request would arrive with filters (potentially empty) in place
        filter_string = "?student=&date_from=2022-07-01&date_to=2022-07-20"
        filter_url = self.path + filter_string

        self.client.force_login(self.teacher)
        response = self.client.get(filter_url)
        actual = str(response.content, encoding='utf8')
        expected = {'points_per_topic': [], 'quizzes_per_topic': []}
        self.assertJSONEqual(actual, expected)


class GetPointsPerDayTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_student', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        cls.path = reverse('data-points-per-day')

    def test_gets_points_per_day_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_points_per_day_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_points_per_day_no_data(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        response_dict = json.loads(response.content)

        # labels should contain an entry for each day in PTS_PER_DAY_DATERANGE
        start_date = datetime.date.today() - datetime.timedelta(PTS_PER_DAY_DATERANGE)
        labels = [str(start_date + datetime.timedelta(num)) for num in range(PTS_PER_DAY_DATERANGE)]
        points = [0 for _ in range(PTS_PER_DAY_DATERANGE)]

        self.assertEquals(response_dict['labels'], labels)
        self.assertEquals(response_dict['datasets'][0]['data'], points)

    def test_points_per_day_no_students(self):
        # Remove any students in the database
        User.objects.filter(is_teacher=False).delete()

        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        response_dict = json.loads(response.content)

        # labels should contain an entry for each day in PTS_PER_DAY_DATERANGE
        start_date = datetime.date.today() - datetime.timedelta(PTS_PER_DAY_DATERANGE)
        labels = [str(start_date + datetime.timedelta(num)) for num in range(PTS_PER_DAY_DATERANGE)]
        points = [0 for _ in range(PTS_PER_DAY_DATERANGE)]

        self.assertEquals(response_dict['labels'], labels)
        self.assertEquals(response_dict['datasets'][0]['data'], points)


class ChartToolsTests(SimpleTestCase):
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
