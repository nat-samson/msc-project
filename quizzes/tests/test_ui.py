import datetime
import json

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By

from quizzes.models import Topic
from users.models import User


class LoginTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome('./chromedriver')
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        super().tearDownClass()

    def setUp(self):
        self.student = User.objects.create_user(username='test_user', password='test_password',
                                                first_name='test', last_name='user')
        self.browser.get(self.live_server_url + reverse('login'))
        self.username_field = self.browser.find_element(By.ID, value='id_username')
        self.password_field = self.browser.find_element(By.ID, value='id_password')
        self.submit_button = self.browser.find_element(By.ID, value='login-button')

    def test_log_in_page_valid_details(self):
        # User types in valid login details and arrives at home page
        self.username_field.send_keys('test_user')
        self.password_field.send_keys('test_password')
        self.submit_button.click()

        # User has been redirected to the home page
        self.assertEquals(
            self.browser.current_url,
            self.live_server_url + reverse("home")
        )
        # a logout button is now present
        self.assertEquals(
            self.browser.find_element(By.LINK_TEXT, "Log out").get_attribute("href"),
            self.live_server_url + reverse("logout")
        )
        # user's name is displayed inside the Navbar on the home page
        self.assertEquals(
            self.browser.find_element(By.XPATH, "//div[@class='navbar-end']/a[1]").text,
            str(self.student)
        )

    def test_log_in_page_invalid_details(self):
        # User types in incorrect password and goes nowhere
        self.username_field.send_keys('test_user')
        self.password_field.send_keys('wrong_password')
        self.submit_button.click()

        # User is still at the login page
        self.assertEquals(
            self.browser.current_url,
            self.live_server_url + reverse('login')
        )
        # Warning is displayed
        warning = self.browser.find_element(By.TAG_NAME, value='li')
        self.assertTrue("Please enter a correct username and password" in warning.text)


class TestsThatRequireLogin(StaticLiveServerTestCase):
    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome('./chromedriver')
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        super().tearDownClass()

    def create_and_login_user(self, is_teacher=False):
        # Create a user and log them into the Selenium session
        self.user = User.objects.create_user(username='test_user', password='test_password',
                                             first_name='test', last_name='user', is_teacher=is_teacher)
        self.client.force_login(self.user)
        session_key = self.client.cookies['sessionid'].value
        self.browser.get(self.live_server_url)
        self.browser.add_cookie({'name': 'sessionid', 'value': session_key, 'path': '/'})

    def test_home_page_student(self):
        # log the student in and visit the homepage
        self.create_and_login_user()
        self.browser.get('%s%s' % (self.live_server_url, reverse('home')))

        # verify that the page looks as it should for students
        # 1) Navbar contains a link to Progress page
        self.assertEquals(
            self.browser.find_element(By.XPATH, value=f"//a[@href='{reverse('progress')}']").text,
            'Progress'
        )

        # 2) There are the same number of cards as (visible) topics
        cards = self.browser.find_elements(By.CLASS_NAME, value="card")
        self.assertEquals(
            len(cards),
            Topic.objects.filter(is_hidden=False, available_from__lte=datetime.date.today()).count()
        )

        # 3) Each card has exactly two buttons
        buttons = cards[1].find_elements(By.CLASS_NAME, value="button")
        self.assertEquals(len(buttons), 2)

    def test_home_page_teacher(self):
        # log the student in and visit the homepage
        self.create_and_login_user(is_teacher=True)
        self.browser.get('%s%s' % (self.live_server_url, reverse('home')))

        # verify that the page looks as it should for teachers
        # 1) Navbar contains a link to Dashboard page
        self.assertEquals(
            self.browser.find_element(By.XPATH, value=f"//a[@href='{reverse('dashboard')}']").text,
            'Dashboard'
        )

        # 2) There is one more card than number of (visible) topics (as first is for editing the database)
        cards = self.browser.find_elements(By.CLASS_NAME, value="card")
        self.assertEquals(
            len(cards),
            Topic.objects.filter(is_hidden=False, available_from__lte=datetime.date.today()).count() + 1
        )

        # 3) The first card is for editing the database
        card_title = cards[0].find_element(By.CLASS_NAME, value='card-header-title').text
        self.assertEquals(card_title, 'Add Quiz Content')

        # 4) Topic cards also have edit buttons
        buttons = cards[1].find_elements(By.CLASS_NAME, value="button")
        self.assertEquals(len(buttons), 4)

    def test_quiz_landing_page(self):
        # log the user in and click the first listed topic's quiz
        self.create_and_login_user()
        self.browser.get('%s%s' % (self.live_server_url, reverse('home')))
        first_quiz_url = reverse('quiz', args=['1'])
        self.browser.find_element(By.XPATH, value=f"//a[@href='{first_quiz_url}']").click()

        # quiz landing page should appear, and display the correct number of upcoming questions
        landing_page = self.browser.find_element(By.ID, value='quiz-landing')
        self.assertTrue(landing_page.is_displayed())

        quiz_data = self.browser.find_element(By.ID, value='quiz-data').get_attribute('innerHTML')
        questions = json.loads(quiz_data)['questions']
        self.assertEquals(len(questions), int(landing_page.find_element(By.TAG_NAME, value='strong').text))

        # Start the quiz, and then the landing page should now be hidden.
        self.browser.find_element(By.ID, value="quiz-start-button").click()
        self.assertFalse(landing_page.is_displayed())

    def test_answering_quiz_questions(self):
        # log the user in and click the first listed topic's quiz, click to start the quiz
        self.create_and_login_user()
        self.browser.get('%s%s' % (self.live_server_url, reverse('home')))
        first_quiz_url = reverse('quiz', args=['1'])
        self.browser.find_element(By.XPATH, value=f"//a[@href='{first_quiz_url}']").click()
        self.browser.find_element(By.ID, value="quiz-start-button").click()

        quiz_data = self.browser.find_element(By.ID, value='quiz-data').get_attribute('innerHTML')
        quiz = json.loads(quiz_data)
        correct_pts = quiz['correct_pts']
        questions = quiz['questions']

        # answer each quiz question in turn
        for num in range(len(questions)):
            current_word = self.browser.find_element(By.ID, value='question-detail').text

            # determine correct answer
            correct = 0
            for question in questions:
                if question['word'] == current_word:
                    current_question = question
                    correct = current_question['correct_answer']
                    break

            options = self.browser.find_element(By.ID, value='options').find_elements(By.TAG_NAME, value="button")
            options[correct].click()

            for i in range(4):
                if i != correct:
                    self.assertNotIn("is-success", options[i].get_attribute("class"))
                else:
                    self.assertIn("is-success", options[i].get_attribute("class"))

            score = self.browser.find_element(By.ID, value='score').text
            self.assertEquals(score, f"{(num + 1) * correct_pts} pts")

            # next question!
            self.browser.find_element(By.ID, value="continue").click()

    def test_answering_quiz_questions_incorrectly(self):
        # log the user in and click the first listed topic's quiz, click to start the quiz
        self.create_and_login_user()
        self.browser.get('%s%s' % (self.live_server_url, reverse('home')))
        first_quiz_url = reverse('quiz', args=['1'])
        self.browser.find_element(By.XPATH, value=f"//a[@href='{first_quiz_url}']").click()
        self.browser.find_element(By.ID, value="quiz-start-button").click()

        quiz_data = self.browser.find_element(By.ID, value='quiz-data').get_attribute('innerHTML')
        quiz = json.loads(quiz_data)
        questions = quiz['questions']

        # answer each quiz question in turn
        for _ in range(len(questions)):
            current_word = self.browser.find_element(By.ID, value='question-detail').text

            # determine correct answer
            correct = 0
            for question in questions:
                if question['word'] == current_word:
                    current_question = question
                    correct = current_question['correct_answer']
                    break

            options = self.browser.find_element(By.ID, value='options').find_elements(By.TAG_NAME, value="button")
            incorrect = (correct + 1) % 4
            options[incorrect].click()

            for i in range(4):
                if i == correct:
                    self.assertIn("is-success", options[i].get_attribute("class"))
                elif i == incorrect:
                    self.assertIn("is-danger", options[i].get_attribute("class"))
                else:
                    self.assertNotIn("is-success", options[i].get_attribute("class"))
                    self.assertNotIn("is-danger", options[i].get_attribute("class"))

            score = self.browser.find_element(By.ID, value='score').text
            self.assertEquals(score, "0 pts")

            # next question!
            self.browser.find_element(By.ID, value="continue").click()
