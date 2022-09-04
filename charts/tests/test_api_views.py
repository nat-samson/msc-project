import datetime
import json
from unittest import SkipTest

from django.test import TestCase
from django.urls import reverse

from charts.chart_data import PTS_PER_DAY_DATERANGE
from quizzes.models import QuizResults, Topic
from users.models import User


class BaseAPIViewTests(TestCase):
    """ Set up some unit and functional tests that check similar aspects of different views. """
    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        cls.path = None

    def setUp(self):
        if self.__class__ == BaseAPIViewTests:
            raise SkipTest('Abstract test. Please ignore.')

        # Adding student afresh each time so can simulate database with no students present
        self.student = User.objects.create_user(username='test_user', password='test_user1234', first_name='test',
                                                last_name='user')
        self.client.force_login(self.student)

    def test_view_status_code(self):
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.path)
        redirect_url = reverse('login') + '?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_when_no_students(self):
        self.student.delete()


class BaseTeachersOnlyAPIViewTests(BaseAPIViewTests):
    """
    As with the BaseAPIViewTests parent class, but logs in the Teacher by default, and checks that students
    are unable to access the view.
    """
    def setUp(self):
        if self.__class__ == BaseTeachersOnlyAPIViewTests:
            raise SkipTest('Abstract test. Please ignore.')

        # Adding student afresh each time so can simulate database with no students present
        self.student = User.objects.create_user(username='test_user', password='test_user1234', first_name='test',
                                                last_name='user')
        self.client.force_login(self.teacher)

    def test_not_accessible_to_students(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        expected = reverse('login') + "?next=" + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected)


class FilteredStudentDataTests(BaseAPIViewTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('filter-date-student')

    def test_filtered_student_json_no_data(self):
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {"points_earned": 0, "quizzes_taken": 0, "correct_pc": "N/A"}
        self.assertJSONEqual(actual, expected)

    def test_when_no_students(self):
        super().test_when_no_students()
        self.client.force_login(self.teacher)
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {"points_earned": 0, "quizzes_taken": 0, "correct_pc": "N/A"}
        self.assertJSONEqual(actual, expected)

    def test_filtered_student_week(self):
        filtered_url = self.path + "?date_range=7"

        # create quiz result, set inside filter range, should be returned
        test_topic = Topic.objects.create(name="Test Topic")
        qr = QuizResults.objects.create(student=self.student, topic=test_topic,
                                        correct_answers=10, incorrect_answers=2, points=999)

        response = self.client.get(filtered_url)
        actual = str(response.content, encoding='utf8')
        expected = {"points_earned": 999, "quizzes_taken": 1, "correct_pc": "83%"}
        self.assertJSONEqual(actual, expected)

        # now set quiz result outside the filter date range (no quiz data should be found)
        qr.date_created = datetime.date.today() - datetime.timedelta(8)
        qr.save()

        new_response = self.client.get(filtered_url)
        actual = str(new_response.content, encoding='utf8')
        expected = {"points_earned": 0, "quizzes_taken": 0, "correct_pc": "N/A"}
        self.assertJSONEqual(actual, expected)


class FilteredTeacherDataTests(BaseTeachersOnlyAPIViewTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('filter-date-teacher')

    def test_when_no_students(self):
        super().test_when_no_students()
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {"active_students": 0, "quizzes_taken": 0, "points_earned": 0}
        self.assertJSONEqual(actual, expected)


class FilteredDataDateTopicTests(BaseTeachersOnlyAPIViewTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('filter-date-topic')

    def test_when_no_students(self):
        super().test_when_no_students()
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = [["No Students Registered!", "N/A"]]
        self.assertJSONEqual(actual, expected)

    def test_filtered_topic(self):
        filtered_url = self.path + "?topic=1"

        # create topic and quiz result, set inside filter range, should be returned
        test_topic = Topic.objects.create(name="Test Topic")
        QuizResults.objects.create(student=self.student, topic=test_topic, points=999)

        response = self.client.get(filtered_url)
        actual = str(response.content, encoding='utf8')
        expected = [["test user", 999]]
        self.assertJSONEqual(actual, expected)

        # now set filter to a different topic
        new_filtered_url = self.path + "?topic=99"

        new_response = self.client.get(new_filtered_url)
        actual = str(new_response.content, encoding='utf8')
        expected = [["test user", 0]]
        self.assertJSONEqual(actual, expected)


class UpdatableChartsTests(BaseAPIViewTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('data-updatable-charts')

    def test_updatable_charts_from_teacher_with_data(self):
        # Add a Quiz Result to the database
        today = datetime.date.today()
        self.animals = Topic.objects.create(name='Animals')
        QuizResults.objects.create(student=self.student, correct_answers=10, incorrect_answers=5,
                                   date_created=today, topic=self.animals, points=100)

        filter_string = f"?student={self.student.pk}&date_to=" + str(today)
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
        response = self.client.get(self.path)
        actual = str(response.content, encoding='utf8')
        expected = {'points_per_topic': [], 'quizzes_per_topic': []}
        self.assertJSONEqual(actual, expected)

    def test_when_no_students(self):
        super().test_when_no_students()

        # teacher request would arrive with filters (potentially empty) in place
        filter_string = "?student=&date_from=2022-07-01&date_to=2022-07-20"
        filter_url = self.path + filter_string

        self.client.force_login(self.teacher)
        response = self.client.get(filter_url)
        actual = str(response.content, encoding='utf8')
        expected = {'points_per_topic': [], 'quizzes_per_topic': []}
        self.assertJSONEqual(actual, expected)


class GetPointsPerDayTests(BaseAPIViewTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('data-points-per-day')

    def test_points_per_day_no_data(self):
        response = self.client.get(self.path)
        response_dict = json.loads(response.content)

        # labels should contain an entry for each day in PTS_PER_DAY_DATERANGE
        start_date = datetime.date.today() - datetime.timedelta(PTS_PER_DAY_DATERANGE)
        labels = [str(start_date + datetime.timedelta(num)) for num in range(PTS_PER_DAY_DATERANGE)]
        points = [0 for _ in range(PTS_PER_DAY_DATERANGE)]

        self.assertEquals(response_dict['labels'], labels)
        self.assertEquals(response_dict['datasets'][0]['data'], points)

    def test_when_no_students(self):
        super().test_when_no_students()
        self.client.force_login(self.teacher)
        self.test_points_per_day_no_data()
