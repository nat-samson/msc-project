import datetime

from django.http import Http404
from django.test import TestCase

from myproject.settings import CORRECT_ANSWER_PTS, ORIGIN_ICON, TARGET_ICON
from quizzes.models import Topic, Word
from quizzes.utils.quiz_builder import _choose_direction, get_quiz, _get_options, _get_dummy_data
from users.models import User


class QuizBuilderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(animals)
        Word.objects.create(origin='Cat', target='die Katze').topics.add(animals)
        Word.objects.create(origin='Dog', target='der Hund').topics.add(animals)
        cls.all_topic_words = Word.objects.filter(topics=animals)

    def test_choose_direction(self):
        self.assertIsInstance(_choose_direction(), bool)

    def test_get_quiz_empty_topic(self):
        empty_topic = Topic.objects.create(name='Empty')
        quiz_data = get_quiz(self.student, empty_topic.pk)
        self.assertIsInstance(quiz_data, dict)
        self.assertEquals(len(quiz_data['questions']), 0)

    def test_get_quiz_topic_with_words(self):
        quiz_data = get_quiz(self.student, 1)
        self.assertIsInstance(quiz_data, dict)
        self.assertEquals(len(quiz_data), 5)

    def test_get_quiz_hidden_topic(self):
        hidden_topic = Topic.objects.create(name='Hidden', long_desc="Can't be seen", is_hidden=True)

        # teachers are permitted to create quizzes for hidden topics (as a demo)
        self.client.force_login(self.teacher)
        quiz_data = get_quiz(self.teacher, hidden_topic.pk)
        self.assertIsInstance(quiz_data, dict)
        self.assertEquals(len(quiz_data['questions']), 0)

        # students are not
        self.client.force_login(self.student)
        with self.assertRaises(Http404):
            get_quiz(self.student, hidden_topic.pk)

    def test_get_quiz_future_scheduled_topic(self):
        week_ahead = datetime.date.today() + datetime.timedelta(7)
        future_topic = Topic.objects.create(name='Future', long_desc="Can't be seen", available_from=week_ahead)

        # teachers are permitted to quiz topics dated in the future (as a demo)
        self.client.force_login(self.teacher)
        quiz_data = get_quiz(self.teacher, future_topic.pk)
        self.assertIsInstance(quiz_data, dict)
        self.assertEquals(len(quiz_data['questions']), 0)

        # students are not
        self.client.force_login(self.student)
        with self.assertRaises(Http404):
            get_quiz(self.student, future_topic.pk)

    def test_get_quiz_format_includes_static_elements(self):
        quiz_data = get_quiz(self.student, 1)
        self.assertEquals(quiz_data['correct_pts'], CORRECT_ANSWER_PTS)
        self.assertEquals(quiz_data['origin_icon'], ORIGIN_ICON)
        self.assertEquals(quiz_data['target_icon'], TARGET_ICON)
        self.assertIsInstance(quiz_data['is_due_revision'], bool)

    def test_get_quiz_questions_format(self):
        quiz = get_quiz(self.student, 1)
        question_keys = {'origin_to_target', 'word', 'options', 'correct_answer', 'word_id'}
        target_words = self.all_topic_words.values_list('target', flat=True)
        origin_words = self.all_topic_words.values_list('origin', flat=True)

        for question in quiz['questions']:
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
        options = _get_options(options_pool, 1, True)
        self.assertIsInstance(options, list)

    def test_get_dummy_data(self):
        # validate the basic format of the dummy data
        dummy_data = _get_dummy_data()
        questions = dummy_data.pop('questions')

        quiz_metadata = {'correct_pts': CORRECT_ANSWER_PTS, 'origin_icon': ORIGIN_ICON,
                         'target_icon': TARGET_ICON, 'is_due_revision': True}
        self.assertDictEqual(dummy_data, quiz_metadata)

        for question in questions:
            question_keys = {'word_id', 'origin_to_target', 'word', 'correct_answer', 'options'}
            self.assertEquals(question.keys(), question_keys)
