import datetime
import json

from django.test import TestCase
from django.urls import reverse, resolve

from quizzes.models import Topic, Word, WordScore, MAX_SCORE, QUIZ_INTERVALS
from quizzes.views import HomeView, TopicDetailView
from users.models import User


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')
        cls.path = reverse('home')

    def test_home_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path, follow=True)
        self.assertEquals(200, response.status_code)

    def test_home_view_url(self):
        view = resolve(self.path)
        self.assertIs(view.func.view_class, HomeView)

    def test_home_template_name(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path, follow=True)
        self.assertTemplateUsed(response, 'quizzes/home.html')

    def test_home_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class TopicDetailPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user to be logged in by each test (topic detail pages require user-specific information)
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')

        # create the topic and words
        test_topic = Topic.objects.create(name='Test Topic', long_desc='This is a test.')
        word_a = Word(origin='test origin a', target='test target a')
        word_b = Word(origin='test origin b', target='test target b')
        word_c = Word(origin='test origin c', target='test target c')
        Word.objects.bulk_create([word_a, word_b, word_c])
        test_topic.words.add(word_a, word_b, word_c)

        # create WordScores (word_b is overdue for revision, word_c has no WordScore)
        WordScore.objects.bulk_create([
            WordScore(student=cls.student, word=word_a),
            WordScore(student=cls.student, word=word_b, next_review=datetime.date.today() - datetime.timedelta(7)),
        ])

        cls.path = reverse('topic_detail', args=[test_topic.pk])



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

    def test_topic_detail_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


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
        fish = Word.objects.create(origin='Fish', target='der Fish')
        cls.mouse.topics.add(animals)
        cls.cat.topics.add(animals)
        dog.topics.add(animals)
        fish.topics.add(animals)

        # Set up USER (a student)
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')

        # Set up WORDSCORE
        # nb no WordScore is created in advance for mouse
        cls.dog_score = WordScore.objects.create(word=dog, student=cls.student, times_seen=10,
                                                 times_correct=5, consecutive_correct=5)

        cls.path = reverse('quiz', args=[animals.pk])

    def test_quiz_view_status(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertEquals(200, response.status_code)

    def test_quiz_template_name(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'quizzes/quiz.html')

    def test_quiz_login_required(self):
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_get_nonexistent_topic_404(self):
        self.client.force_login(self.student)
        path = reverse('quiz', args=['100'])
        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)

    def test_topic_with_fewer_than_4_words_redirects_home(self):
        empty_topic = Topic.objects.create(name='Empty')
        self.client.force_login(self.student)
        path = reverse('quiz', args=[empty_topic.pk])
        response = self.client.get(path, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_quiz_form_inputs(self):
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        self.assertContains(response, 'csrfmiddlewaretoken', 1)
        self.assertContains(response, 'type="hidden"', 2)  # includes the CSRF token and the hidden JSON field

        # form must have no extra inputs beyond those specified above
        self.assertContains(response, '<input type=', 2)

    def test_quiz_results_new_question_correct(self):
        # No WordScore exists for this word / user combination
        self.client.force_login(self.student)
        quiz_results = {
            str(self.mouse.id): True
        }
        results = json.dumps(quiz_results)
        self.client.post(self.path, {'results': results})

        # check score has been saved in database
        word_score = WordScore.objects.get(word_id=1, student=self.student)
        self.assertEquals(1, word_score.consecutive_correct)
        self.assertEquals(1, word_score.times_seen)
        self.assertEquals(1, word_score.times_correct)
        self.assertEquals(self.tomorrow, word_score.next_review)

    def test_quiz_results_new_question_incorrect(self):
        # No WordScore exists for this word / user combination
        self.client.force_login(self.student)
        quiz_results = {
            str(self.mouse.id): False
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
            str(cat_score.word_id): True
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
            str(cat_score.word_id): False
        }
        results = json.dumps(quiz_results)
        self.client.post(self.path, {'results': results})

        # check that the WordScore has changed for cat/student
        cat_score.refresh_from_db()
        self.assertEquals(3, cat_score.times_correct)
        self.assertEquals(0, cat_score.consecutive_correct)
        self.assertEquals(6, cat_score.times_seen)
        self.assertEquals(self.today, cat_score.next_review)

    def test_quiz_results_due_review_correct(self):
        # cat_score is due for review today, getting it correct should update its schedule and score
        self.client.force_login(self.student)
        cat_score = WordScore.objects.create(word=self.cat, student=self.student, times_correct=3, times_seen=5,
                                             next_review=self.today, consecutive_correct=3)
        quiz_results = {
            str(cat_score.word_id): True
        }
        results = json.dumps(quiz_results)
        self.client.post(self.path, {'results': results})

        # cat score and schedule should be updated
        next_review = self.today + datetime.timedelta(QUIZ_INTERVALS[min(cat_score.consecutive_correct, MAX_SCORE)])
        cat_score.refresh_from_db()

        self.assertEquals(4, cat_score.consecutive_correct)
        self.assertEquals(6, cat_score.times_seen)
        self.assertEquals(4, cat_score.times_correct)
        self.assertEquals(next_review, cat_score.next_review)

    def test_quiz_results_due_review_incorrect(self):
        # cat_score is due for review today, getting it incorrect should reset progress
        self.client.force_login(self.student)
        cat_score = WordScore.objects.create(word=self.cat, student=self.student, times_correct=3, times_seen=5,
                                             next_review=self.today, consecutive_correct=3)
        quiz_results = {
            str(cat_score.word_id): False
        }
        results = json.dumps(quiz_results)
        self.client.post(self.path, {'results': results})

        # cat score and schedule should be updated
        next_review = self.today
        cat_score.refresh_from_db()

        self.assertEquals(0, cat_score.consecutive_correct)
        self.assertEquals(6, cat_score.times_seen)
        self.assertEquals(3, cat_score.times_correct)
        self.assertEquals(next_review, cat_score.next_review)

    def test_session_with_results_data_leads_to_results_page(self):
        self.client.force_login(self.student)
        session = self.client.session
        session['results'] = {'correct': 5, 'total': 5}
        session.save()
        response = self.client.get(self.path, follow=True)
        self.assertTemplateUsed(response, 'quizzes/quiz_results.html')
