from django.test import TestCase
from django.urls import reverse, resolve

from .models import Topic, Word
from .views import home


class HomeTests(TestCase):
    def test_home_view_status(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_view_url(self):
        view = resolve('/')
        self.assertEquals(view.func, home)


class TopicModelTests(TestCase):
    def setUp(self):
        Topic.objects.create(name='Animals', description='Practice your German words for Animals.')
        Topic.objects.create(name='Colours', description='All the colours of des Regenbogens.')

    def test_topics_str(self):
        # test __str__ for Topics
        animals = Topic.objects.get(name="Animals")
        colours = Topic.objects.get(name="Colours")
        self.assertEqual(str(animals), 'Animals')
        self.assertEqual(str(colours), 'Colours')


class WordModelTests(TestCase):
    def setUp(self):
        Topic.objects.create(name='Animals', description='Practice your German words for Animals.')
        animals = Topic.objects.get(name='Animals')
        Word.objects.create(origin='Mouse', target='die Maus', topic=animals)
        Word.objects.create(origin='Fish', target='der Fisch', topic=animals)

    def test_words_str(self):
        # test __str__ for Words
        mouse = Word.objects.get(origin="Mouse")
        fish = Word.objects.get(origin="Fish")
        self.assertEqual(str(mouse), 'Mouse: die Maus')
        self.assertEqual(str(fish), 'Fish: der Fisch')

    def test_words_via_origin_target(self):
        # test that origin and target both lead to correct Word
        mouse = Word.objects.get(origin="Mouse")
        mouse_via_maus = Word.objects.get(target='die Maus')
        self.assertEqual(mouse, mouse_via_maus)
