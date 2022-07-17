import datetime
import json

from django.test import TestCase
from django.urls import reverse, resolve

from users.models import User
from .models import Topic, Word, WordScore, MAX_SCORE
from .views import TopicListView, TopicDetailView
from .quiz_builder import choose_direction, get_quiz, get_options


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234', is_student=True)
        cls.url = reverse('home')

    def test_home_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url, follow=True)
        self.assertEquals(200, response.status_code)

    def test_home_view_url(self):
        view = resolve('/')
        self.assertIs(view.func.view_class, TopicListView)

    def test_home_template_name(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'quizzes/home.html')

    def test_home_login_required(self):
        response = self.client.get(self.url, follow=False)
        redirect_url = self.url + 'login/?next=/'
        self.assertRedirects(response, redirect_url)


class TopicDetailPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create the topic
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        cls.path = '/topic/' + str(animals.pk) + '/'

        # Create a user to be logged in by each test (topic detail pages require user-specific information)
        cls.student = User.objects.create_user(username='test_user', password='test_user1234', is_student=True)

    def test_topic_detail_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_topic_detail_view_url(self):
        view = resolve(self.path)
        self.assertIs(view.func.view_class, TopicDetailView)

    def test_topic_detail_view_template(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'quizzes/topic_detail.html')


class TopicModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        cls.colours = Topic.objects.create(name='Colours', long_desc='All the colours of des Regenbogens.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(cls.animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(cls.animals)

    def test_topic_str(self):
        # test __str__ for Topic model
        self.assertEqual('Animals', str(self.animals))
        self.assertEqual('Colours', str(self.colours))

    def test_topic_word_count(self):
        self.assertEqual(2, self.animals.words.count())
        self.assertEqual(0, self.colours.words.count())


class WordModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(animals)
        cls.mouse = Word.objects.get(origin="Mouse")
        cls.fish = Word.objects.get(origin="Fish")

    def test_word_str(self):
        # test __str__ for Word model
        self.assertEqual('Mouse -> die Maus', str(self.mouse))
        self.assertEqual('Fish -> der Fisch', str(self.fish))

    def test_word_via_origin_target(self):
        # test that origin and target both lead to correct Word
        mouse_via_maus = Word.objects.get(target='die Maus')
        self.assertEqual(self.mouse, mouse_via_maus)


class WordScoreModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        cls.mouse = Word.objects.create(origin='Mouse', target='die Maus')
        cls.mouse.topics.add(animals)
        cls.student = User.objects.create_user(username='test_user', password='test_user1234', is_student=True)
        cls.mouse_score = WordScore.objects.create(word=cls.mouse, student=cls.student)

    def test_word_score_str(self):
        # test __str__ for WordScore
        expected = f'{self.student} / {self.mouse}: 0'
        self.assertEqual(expected, str(self.mouse_score))

    def test_word_score_score(self):
        # maximum possible score is capped by whatever is set as MAX_SCORE
        for num in range(MAX_SCORE + 2):
            self.mouse_score.consecutive_correct = num
            self.mouse_score.save()
            expected = min(num, MAX_SCORE)
            self.assertEqual(expected, self.mouse_score.score())


class QuizTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.today = datetime.date.today()
        cls.tomorrow = cls.today + datetime.timedelta(days=1)

        # Set up TOPIC and WORD
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        cls.mouse = Word.objects.create(origin='Mouse', target='die Maus')
        cls.cat = Word.objects.create(origin='Cat', target='die Katze')
        dog = Word.objects.create(origin='Dog', target='der Hund')
        cls.mouse.topics.add(animals)
        cls.cat.topics.add(animals)
        dog.topics.add(animals)

        # Set up USER (a student)
        cls.student = User.objects.create_user(username='test_user', password='test_user1234', is_student=True)

        # Set up WORDSCORE
        # nb no WordScore is created in advance for mouse
        cls.dog_score = WordScore.objects.create(word=dog, student=cls.student, times_seen=10,
                                                 times_correct=5, consecutive_correct=5)

        cls.path = f'/quiz/{animals.pk}/'

    def test_quiz_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_quiz_template_name(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'quizzes/quiz.html')

    def test_quiz_form_inputs(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertContains(response, 'csrfmiddlewaretoken', 1)
        self.assertContains(response, 'type="hidden"', 2)  # includes the CSRF token and the hidden JSON field

        # form must have no extra inputs beyond those specified above
        self.assertContains(response, '<input type=', 2)

    def test_quiz_results_question_correct(self):
        # No WordScore exists for this word / user combination
        self.client.force_login(self.student)
        quiz_results = {
            '1': True
        }
        results = json.dumps(quiz_results)

        self.client.post(self.path, {'results': results})

        # check score has been saved in database
        word_score = WordScore.objects.get(word_id=1, student=self.student)
        self.assertEquals(1, word_score.consecutive_correct)
        self.assertEquals(1, word_score.times_seen)
        self.assertEquals(1, word_score.times_correct)
        self.assertEquals(self.tomorrow, word_score.next_review)

    def test_quiz_results_question_incorrect(self):
        # No WordScore exists for this word / user combination
        self.client.force_login(self.student)
        quiz_results = {
            '1': False
        }
        results = json.dumps(quiz_results)

        self.client.post(self.path, {'results': results})

        # check score has been saved in database
        word_score = WordScore.objects.get(word_id=1, student=self.student)
        self.assertEquals(0, word_score.consecutive_correct)
        self.assertEquals(1, word_score.times_seen)
        self.assertEquals(0, word_score.times_correct)
        self.assertEquals(self.today, word_score.next_review)

    def test_quiz_results_not_due_review_correct(self):
        # cat_score is due for review tomorrow, so this is an optional extra revision session
        # getting it correct DOES NOT affect the word_score in such situations
        self.client.force_login(self.student)
        cat_score = WordScore.objects.create(word=self.cat, student=self.student, times_correct=3, times_seen=5,
                                             next_review=self.tomorrow, consecutive_correct=3)
        quiz_results = {
            '2': True
        }
        results = json.dumps(quiz_results)
        self.client.post(self.path, {'results': results})

        # check that nothing has changed with the WordScore for cat/student
        cat_score.refresh_from_db()
        self.assertEquals(3, cat_score.consecutive_correct)
        self.assertEquals(5, cat_score.times_seen)
        self.assertEquals(3, cat_score.times_correct)
        self.assertEquals(self.tomorrow, cat_score.next_review)

    def test_quiz_results_not_due_review_incorrect(self):
        # cat_score is due for review tomorrow, so this is an optional extra revision session
        # getting it incorrect DOES affect the WordScore
        self.client.force_login(self.student)
        cat_score = WordScore.objects.create(word=self.cat, student=self.student, times_correct=3, times_seen=5,
                                             next_review=self.tomorrow, consecutive_correct=3)
        quiz_results = {
            '2': False
        }
        results = json.dumps(quiz_results)
        self.client.post(self.path, {'results': results})

        # check that the WordScore has changed for cat/student
        cat_score.refresh_from_db()
        self.assertEquals(3, cat_score.times_correct)
        self.assertEquals(0, cat_score.consecutive_correct)
        self.assertEquals(6, cat_score.times_seen)
        self.assertEquals(self.tomorrow, cat_score.next_review)


class QuizBuilderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234', is_student=True)
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(animals)
        Word.objects.create(origin='Cat', target='die Katze').topics.add(animals)
        Word.objects.create(origin='Dog', target='der Hund').topics.add(animals)
        cls.all_topic_words = Word.objects.filter(topics=animals)

    def test_choose_direction(self):
        self.assertIsInstance(choose_direction(), bool)

    def test_get_quiz_empty_topic(self):
        empty_topic = Topic.objects.create(name='Empty')
        quiz = get_quiz(self.student, empty_topic.pk)
        self.assertIsInstance(quiz, list)
        self.assertEquals(len(quiz), 0)

    def test_get_quiz_topic_with_words(self):
        quiz = get_quiz(self.student, 1)
        self.assertIsInstance(quiz, list)
        self.assertEquals(len(quiz), 4)

    def test_get_quiz_output_format(self):
        quiz = get_quiz(self.student, 1)
        question_keys = {'origin_to_target', 'word', 'options', 'correct_answer', 'word_id'}
        target_words = self.all_topic_words.values_list('target', flat=True)
        origin_words = self.all_topic_words.values_list('origin', flat=True)

        for question in quiz:
            # all expected keys in place
            self.assertEquals(question_keys, set(question))

            # ensure word is valid
            word = Word.objects.get(pk=question['word_id'])

            # ensure 4 unique multiple choice options were generated
            options = question['options']
            self.assertEquals(4, len(set(options)))

            # other elements depend on the question 'direction'
            direction = question['origin_to_target']
            self.assertIsInstance(direction, bool)

            correct_index = question['correct_answer']

            if direction:
                self.assertEquals(word.origin, question['word'])

                # checks that all multiple choice options are valid
                for option in options:
                    self.assertIn(option, target_words)

                # check that 'correct_answer' does lead to correct answer
                self.assertEquals(word.target, options[correct_index])

            # as above but when word is being quizzed in opposite direction
            else:
                self.assertEquals(word.target, question['word'])
                for option in options:
                    self.assertIn(option, origin_words)
                self.assertEquals(word.origin, options[correct_index])

    def test_get_options(self):
        options_pool = list(self.all_topic_words.values('id', 'origin', 'target'))
        options = get_options(options_pool, 1, True)
        self.assertIsInstance(options, list)
