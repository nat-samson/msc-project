import datetime
import time

import chromedriver_autoinstaller
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from quizzes.models import Topic, QuizResults
from users.models import User


def update_dropdown(dropdown, button, value):
    """ Update the selected value on a Select input """
    dropdown.select_by_value(value)
    button.click()

    # Give the page time to load
    time.sleep(0.5)


def create_quiz_data(student, topic1, topic2):
    """ Add some QuizResults data to the database """
    QuizResults.objects.bulk_create(
        [
            QuizResults(student=student, topic=topic1, points=1000,
                        date_created=datetime.date.today(), correct_answers=10, incorrect_answers=2),
            QuizResults(student=student, topic=topic2, points=100,
                        date_created=datetime.date.today() - datetime.timedelta(6), correct_answers=12,
                        incorrect_answers=0),
            QuizResults(student=student, topic=topic1, points=10,
                        date_created=datetime.date.today() - datetime.timedelta(28), correct_answers=6,
                        incorrect_answers=6),
            QuizResults(student=student, topic=topic2, points=1,
                        date_created=datetime.date.today() - datetime.timedelta(35), correct_answers=8,
                        incorrect_answers=4)
        ]
    )


class BaseUITestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # create a student and a teacher, Topics
        cls.student = User.objects.create_user(username='seleniumstudent', password='test_password',
                                               first_name='test', last_name='student')
        cls.student_b = User.objects.create_user(username='seleniumstudentb', password='test_password',
                                                 first_name='test_b', last_name='student_b')
        cls.teacher = User.objects.create_user(username='seleniumteacher', password='test_password',
                                               first_name='test', last_name='teacher', is_teacher=True)
        cls.topic1 = Topic.objects.create(name='Selenium Test Topic 1')
        cls.topic2 = Topic.objects.create(name='Selenium Test Topic 2')

        # set up automated Selenium browser
        chromedriver_autoinstaller.install()
        cls.browser = webdriver.Chrome()
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        super().tearDownClass()

    def login_user(self, user):
        self.client.force_login(user)
        session_key = self.client.cookies['sessionid'].value
        self.browser.get(self.live_server_url)
        self.browser.add_cookie({'name': 'sessionid', 'value': session_key, 'path': '/'})


class ProgressUITests(BaseUITestCase):
    fixtures = ['dump.json']

    def setUp(self):
        # Create some Quiz Results data
        create_quiz_data(self.student, self.topic1, self.topic2)

        # log the student in and visit the Progress page
        self.login_user(self.student)
        self.browser.get('%s%s' % (self.live_server_url, reverse('progress')))

    def test_progress_filters(self):
        # Get the dropdown menu and submit button
        date_filter = Select(self.browser.find_element(By.ID, 'id_date_range'))
        submit_button = self.browser.find_element(By.ID, 'filter-submit')

        # Get the initial data from the filterable boxes
        points = self.browser.find_element(By.ID, value='points-box').find_element(By.CLASS_NAME, value='title')
        quizzes = self.browser.find_element(By.ID, value='quizzes-box').find_element(By.CLASS_NAME, value='title')
        pc = self.browser.find_element(By.ID, value='pc-correct-box').find_element(By.CLASS_NAME, value='title')

        # initially, page is set to all-time data
        self.assertEquals('All Time', date_filter.first_selected_option.text)
        self.assertEquals('1111', points.text)
        self.assertEquals('4', quizzes.text)
        self.assertEquals('75%', pc.text)

        # set the filter to Today
        update_dropdown(date_filter, submit_button, '0')
        self.assertEquals('1000', points.text)
        self.assertEquals('1', quizzes.text)
        self.assertEquals('83%', pc.text)

        # set the filter to last week
        update_dropdown(date_filter, submit_button, '7')
        self.assertEquals('1100', points.text)
        self.assertEquals('2', quizzes.text)
        self.assertEquals('92%', pc.text)

        # set the filter to last month
        update_dropdown(date_filter, submit_button, '30')
        self.assertEquals('1110', points.text)
        self.assertEquals('3', quizzes.text)
        self.assertEquals('78%', pc.text)


class DashboardUITests(BaseUITestCase):
    def setUp(self):
        # Create some Quiz Results data for both students
        create_quiz_data(self.student, self.topic1, self.topic2)
        create_quiz_data(self.student_b, self.topic1, self.topic2)

        # log the Teacher in and visit the Dashboard
        self.login_user(self.teacher)
        self.browser.get('%s%s' % (self.live_server_url, reverse('dashboard')))

    def test_dashboard_databox_filters(self):
        # Get the dropdown menu and submit button
        date_filter = Select(self.browser.find_element(By.ID, 'id_date_range'))
        submit_button = self.browser.find_element(By.ID, 'filter-submit')

        # Get the initial data from the filterable boxes
        students = self.browser.find_element(By.ID, value='students-box').find_element(By.CLASS_NAME, value='title')
        quizzes = self.browser.find_element(By.ID, value='quizzes-box').find_element(By.CLASS_NAME, value='title')
        points = self.browser.find_element(By.ID, value='points-box').find_element(By.CLASS_NAME, value='title')

        # initially, page is set to all-time data
        self.assertEquals('All Time', date_filter.first_selected_option.text)
        self.assertEquals('2', students.text)
        self.assertEquals('8', quizzes.text)
        self.assertEquals('2222', points.text)

        # set the filter to Today
        update_dropdown(date_filter, submit_button, '0')
        self.assertEquals('2', students.text)
        self.assertEquals('2', quizzes.text)
        self.assertEquals('2000', points.text)

        # set the filter to last week
        update_dropdown(date_filter, submit_button, '7')
        self.assertEquals('2', students.text)
        self.assertEquals('4', quizzes.text)
        self.assertEquals('2200', points.text)

        # set the filter to last month
        update_dropdown(date_filter, submit_button, '30')
        self.assertEquals('2', students.text)
        self.assertEquals('6', quizzes.text)
        self.assertEquals('2220', points.text)


class DashboardUITestsB(BaseUITestCase):
    # Put this into a separate class to avoid race condition with other Dashboard UI Test until a way around is found.
    def setUp(self):
        # Create some Quiz Results data for both students
        create_quiz_data(self.student, self.topic1, self.topic2)
        create_quiz_data(self.student_b, self.topic1, self.topic2)

        # log the Teacher in and visit the Dashboard
        self.login_user(self.teacher)
        self.browser.get('%s%s' % (self.live_server_url, reverse('dashboard')))

    def test_points_per_student(self):
        # Get the dropdown menus and submit button
        topic_filter = Select(self.browser.find_element(By.ID, 'id_topic'))
        date_filter = Select(self.browser.find_element(By.ID, 'topic-filter-form').find_element(By.ID, 'id_date_range'))
        submit_button = self.browser.find_element(By.ID, 'topic-filter-submit')

        # Get the points table's rows
        table_body = self.browser.find_element(By.ID, 'points-table').find_element(By.TAG_NAME, 'tbody')
        rows = table_body.find_elements(By.TAG_NAME, 'tr')

        # No filters
        first_row = rows[0].find_elements(By.TAG_NAME, 'td')
        self.assertEquals('test student', first_row[0].text)
        self.assertEquals('1111', first_row[1].text)

        second_row = rows[1].find_elements(By.TAG_NAME, 'td')
        self.assertEquals('test_b student_b', second_row[0].text)
        self.assertEquals('1111', second_row[1].text)

        # Filter topic
        update_dropdown(topic_filter, submit_button, str(self.topic1.pk))
        rows = table_body.find_elements(By.TAG_NAME, 'tr')
        first_row = rows[0].find_elements(By.TAG_NAME, 'td')
        self.assertEquals('test student', first_row[0].text)
        self.assertEquals('1010', first_row[1].text)

        # Filter date
        update_dropdown(date_filter, submit_button, '0')
        rows = table_body.find_elements(By.TAG_NAME, 'tr')
        first_row = rows[0].find_elements(By.TAG_NAME, 'td')
        self.assertEquals('test student', first_row[0].text)
        self.assertEquals('1000', first_row[1].text)
