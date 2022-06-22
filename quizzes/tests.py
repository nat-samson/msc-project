from django.test import TestCase
from django.urls import reverse, resolve
from .models import Topic, Word
from .views import TopicListView


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


class TopicModelTests(TestCase):
    def setUp(self):
        self.animals = Topic.objects.create(name='Animals', description='Practice your German words for Animals.')
        self.colours = Topic.objects.create(name='Colours', description='All the colours of des Regenbogens.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(self.animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(self.animals)

    def test_topics_str(self):
        # test __str__ for Topics
        self.assertEqual('Animals', str(self.animals))
        self.assertEqual('Colours', str(self.colours))

    def test_topic_word_count(self):
        self.assertEqual(2, self.animals.words.count())
        self.assertEqual(0, self.colours.words.count())


class WordModelTests(TestCase):
    def setUp(self):
        animals = Topic.objects.create(name='Animals', description='Practice your German words for Animals.')
        Word.objects.create(origin='Mouse', target='die Maus').topics.add(animals)
        Word.objects.create(origin='Fish', target='der Fisch').topics.add(animals)
        self.mouse = Word.objects.get(origin="Mouse")
        self.fish = Word.objects.get(origin="Fish")

    def test_words_str(self):
        # test __str__ for Words
        self.assertEqual('Mouse -> die Maus', str(self.mouse))
        self.assertEqual('Fish -> der Fisch', str(self.fish))

    def test_words_via_origin_target(self):
        # test that origin and target both lead to correct Word
        mouse_via_maus = Word.objects.get(target='die Maus')
        self.assertEqual(self.mouse, mouse_via_maus)
