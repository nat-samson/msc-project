from django.test import TestCase
from django.urls import reverse, resolve

from users.models import User
from .models import Topic, Word, WordScore, MAX_SCORE
from .views import TopicListView, TopicDetailView


class HomeTests(TestCase):
    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status(self):
        self.assertEquals(200, self.response.status_code)

    def test_home_view_url(self):
        view = resolve('/')
        self.assertIs(view.func.view_class, TopicListView)

    def test_home_template_name(self):
        self.assertTemplateUsed(self.response, 'quizzes/home.html')


class TopicPageTests(TestCase):
    def setUp(self):
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        path = '/topic/' + str(animals.pk) + '/'
        self.view = resolve(path)

    def test_home_view_url(self):
        self.assertIs(self.view.func.view_class, TopicDetailView)


class TopicModelTests(TestCase):
    def setUp(self):
        self.animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        self.colours = Topic.objects.create(name='Colours', long_desc='All the colours of des Regenbogens.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(self.animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(self.animals)

    def test_topic_str(self):
        # test __str__ for Topic model
        self.assertEqual('Animals', str(self.animals))
        self.assertEqual('Colours', str(self.colours))

    def test_topic_word_count(self):
        self.assertEqual(2, self.animals.words.count())
        self.assertEqual(0, self.colours.words.count())


class WordModelTests(TestCase):
    def setUp(self):
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(animals)
        self.mouse = Word.objects.get(origin="Mouse")
        self.fish = Word.objects.get(origin="Fish")

    def test_word_str(self):
        # test __str__ for Word model
        self.assertEqual('Mouse -> die Maus', str(self.mouse))
        self.assertEqual('Fish -> der Fisch', str(self.fish))

    def test_word_via_origin_target(self):
        # test that origin and target both lead to correct Word
        mouse_via_maus = Word.objects.get(target='die Maus')
        self.assertEqual(self.mouse, mouse_via_maus)


class WordScoreModelTests(TestCase):
    def setUp(self):
        animals = Topic.objects.create(name='Animals', long_desc='Practice your German words for Animals.')
        self.mouse = Word.objects.create(origin='Mouse', target='die Maus')
        self.mouse.topics.add(animals)
        self.student = User.objects.create_user(username='testuser', password='testuser1234',
                                                first_name='test', last_name='user')
        self.mouse_score = WordScore.objects.create(word=self.mouse, student=self.student)

    def test_word_score_str(self):
        # test __str__ for WordScore
        expected = f'{self.student} / {self.mouse}: 0'
        self.assertEqual(expected, str(self.mouse_score))

    def test_word_score_score(self):
        # maximum possible score is capped by whatever is set as MAX_SCORE
        for num in range(MAX_SCORE + 2):
            self.mouse_score.consecutive_correct = num
            expected = min(num, MAX_SCORE)
            self.assertEqual(expected, self.mouse_score.score)
