import datetime

from django.test import TestCase

from quizzes.models import Topic, Word, WordScore, MAX_SCORE, QuizResults, QUIZ_INTERVALS
from users.models import User


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
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')

    def setUp(self):
        # mouse_score is changed by tests, so recreate it afresh each time
        self.mouse_score = WordScore.objects.create(word=self.mouse, student=self.student)

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

    def test_word_score_set_next_review(self):
        # date of next review should increase according to preset quiz intervals and current score
        today = datetime.date.today()

        for i in range(len(QUIZ_INTERVALS)):
            self.mouse_score.consecutive_correct = i
            self.mouse_score.save()
            self.mouse_score.set_next_review()
            interval = QUIZ_INTERVALS[i]
            expected = today + datetime.timedelta(interval)
            self.assertEqual(expected, self.mouse_score.next_review)


class QuizResultsModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        cls.student = User.objects.create_user(first_name='test', last_name='user',
                                               username='test_user', password='test_user1234')
        cls.qr = QuizResults.objects.create(student=cls.student, topic=cls.animals)

    def setUp(self):
        # recreate this student afresh each test
        self.new_student = User.objects.create_user(username='new')

    def test_quiz_results_str(self):
        # test __str__ for QuizResults
        today = datetime.date.today()
        expected = "Quiz Results: test user / Animals on " + str(today)
        self.assertEqual(expected, str(self.qr))

    def test_get_user_streak_no_data(self):
        # new student has no quiz data, so streak is 0
        actual = QuizResults.get_user_streak(self.new_student)
        self.assertEqual(0, actual)

    def test_get_broken_streak(self):
        # give user 100 day streak, but no quiz today or yesterday
        self.new_student.streak = 100
        self.new_student.save()
        broken_streak = QuizResults.get_user_streak(self.new_student)
        self.assertEqual(0, broken_streak)

    def test_continue_existing_streak(self):
        # user is adding to their 100-day streak
        self.new_student.streak = 100
        self.new_student.save()

        # add quiz results data for yesterday, so quizzing again today builds on it
        yesterday = datetime.date.today() - datetime.timedelta(1)
        qr = QuizResults.objects.create(student=self.new_student, topic=self.animals)
        qr.date_created = yesterday
        qr.save()

        QuizResults.update_user_streak(self.new_student)
        self.new_student.refresh_from_db()
        streak = QuizResults.get_user_streak(self.new_student)
        self.assertEqual(101, streak)

    def test_update_streak_when_already_quizzed_today(self):
        # streak should not increase in length if the user has already quizzed today
        self.new_student.streak = 100
        self.new_student.save()

        # add quiz results data for today
        qr = QuizResults.objects.create(student=self.new_student, topic=self.animals)
        qr.date_created = datetime.date.today()
        qr.save()

        QuizResults.update_user_streak(self.new_student)
        self.new_student.refresh_from_db()
        streak = QuizResults.get_user_streak(self.new_student)
        self.assertEqual(100, streak)
