import datetime
import http.client
from unittest import SkipTest

from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse, resolve

from editor.forms import TopicForm, WordFilterForm, WordUpdateForm
from editor.views import TopicCreateView, TopicWordsView, add_word, get_filtered_words, WordUpdateView, \
    TopicUpdateView, TopicDeleteView, WordDeleteView
from quizzes.models import Topic, Word
from users.models import User


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username='test_user', password='test_user1234')
        cls.teacher = User.objects.create_user(username='test_teacher', password='test_user1234', is_teacher=True)

        # override these as necessary in each test class
        cls.path = None
        cls.view_class = None
        cls.func = None
        cls.template_path = None

    def setUp(self):
        self.client.force_login(self.teacher)

        # Mark tests as abstract unless they are members of a BaseTestCase subclass
        if self.__class__ == BaseTestCase:
            raise SkipTest('Abstract test. Please ignore.')

    def test_view_status(self):
        response = self.client.get(self.path, follow=True)
        self.assertEquals(200, response.status_code)

    def test_view_url(self):
        view = resolve(self.path)
        if self.view_class:
            self.assertIs(view.func.view_class, self.view_class)
        else:
            self.assertIs(view.func, self.func)

    def test_template_name(self):
        response = self.client.get(self.path, follow=True)
        self.assertTemplateUsed(response, self.template_path)

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.path)
        redirect_url = '/login/?next=' + self.path
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_not_accessible_to_students(self):
        # a student attempting to access topic create are denied
        self.client.force_login(self.student)
        response = self.client.get(self.path)
        response.user = self.student

        if self.view_class:
            with self.assertRaises(PermissionDenied):
                self.view_class.as_view()(response)
        else:
            self.assertEqual(response.status_code, 302)

    def test_accessible_to_teachers(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, http.client.OK)


class TopicCreateTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('topic_create')
        cls.view_class = TopicCreateView
        cls.template_path = 'editor/topic_form.html'

    def test_topic_create_includes_form(self):
        response = self.client.get(self.path)
        topic_create_form = response.context.get('form')
        self.assertIsInstance(topic_create_form, TopicForm)

    def test_topic_create_form_fields(self):
        response = self.client.get(self.path)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'type="text"', 2)
        self.assertContains(response, 'class="textarea"', 1)
        self.assertContains(response, 'type="date"', 1)
        self.assertContains(response, 'type="checkbox"', 1)
        self.assertContains(response, 'type="submit"', 1)

        # form must have no extra inputs beyond those specified above
        self.assertContains(response, '<input type=', 7)

    def test_topic_create_successful(self):
        self.client.post(self.path, {'name': 'Test Topic', 'available_from': datetime.date.today(), "short_desc": "sd"})
        self.assertTrue(Topic.objects.filter(name='Test Topic').exists())


class TopicWordsViewAllTopicsTests(BaseTestCase):
    """ Tests the TopicWordsView page when visiting via 'View All Words', so without a URL parameter """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('topic_words')
        cls.view_class = TopicWordsView
        cls.template_path = 'editor/topic_words.html'


class TopicWordsViewSingleTopicTests(BaseTestCase):
    """ Tests the TopicWordsView page when visiting a specified topic, so with a URL parameter """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create two topics, each with a single unique word
        test_topic_a = Topic(name='Test Topic A', long_desc='This is a test.')
        test_topic_b = Topic(name='Test Topic B', long_desc='This is a test.')
        Topic.objects.bulk_create([test_topic_a, test_topic_b])
        word_a = Word(origin='origin A', target='origin A')
        word_b = Word(origin='origin B', target='origin B')
        Word.objects.bulk_create([word_a, word_b])
        test_topic_a.words.add(word_a)
        test_topic_b.words.add(word_b)

        cls.path = reverse('topic_words', kwargs={'topic_id': test_topic_a.pk})
        cls.path_no_argument = reverse('topic_words')
        cls.view_class = TopicWordsView
        cls.template_path = 'editor/topic_words.html'

    def test_page_contains_only_words_from_correct_topic(self):
        response = self.client.get(self.path)
        self.assertContains(response, 'origin A')
        self.assertNotContains(response, 'origin B')

    def test_unfiltered_page_contains_words_all_topics(self):
        response = self.client.get(self.path_no_argument)
        self.assertContains(response, 'origin A')
        self.assertContains(response, 'origin B')

    def test_page_does_not_contain_word_filter_form(self):
        response = self.client.get(self.path)
        form = response.context.get('word_filter_form', None)
        self.assertIsNone(form)

    def test_unfiltered_page_does_contain_word_filter_form(self):
        response = self.client.get(self.path_no_argument)
        form = response.context.get('word_filter_form', None)
        self.assertIsInstance(form, WordFilterForm)


class AddWordTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_topic = Topic.objects.create(name='Test Topic', long_desc='This is a test.')
        cls.path = reverse('add_word', kwargs={'topic_id': cls.test_topic.pk})
        cls.func = add_word
        cls.template_path = 'editor/word_include_form.html'

    def test_word_create_successful(self):
        self.client.post(self.path, {'origin': 'test origin', 'target': 'test target'})
        created_word = Word.objects.get(origin='test origin', target='test target')

        # test that it was added to the Topic of the appropriate page
        self.assertIn(self.test_topic, created_word.topics.all())

    def test_word_create_unsuccessful(self):
        Word.objects.create(origin='test origin', target='test target')
        response = self.client.post(self.path, {'origin': 'test origin', 'target': 'test target'})
        self.assertContains(response, 'Word with this Origin already exists.')

    def test_word_create_no_topic_page(self):
        # feature not currently in use. Only possible when the quick 'add word' feature is available on all topics page.
        path_all_topics = reverse('add_word')
        self.client.post(path_all_topics, {'origin': 'test origin', 'target': 'test target'})
        created_word = Word.objects.get(origin='test origin', target='test target')

        # the Word should not be a member of any Topic
        associated_topics = created_word.topics.all()
        self.assertEquals(len(associated_topics), 0)


class GetFilteredWordsTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.path = reverse('filter_words')
        cls.func = get_filtered_words
        cls.template_path = 'editor/word_list.html'

        # create a Topic, some Words, and assign only one Word to the Topic
        cls.test_topic = Topic.objects.create(name='Test Topic', long_desc='This is a test.')
        word_a = Word(origin='test origin a', target='test target a')
        Word.objects.bulk_create([
            word_a,
            Word(origin='test origin b', target='test target b'),
            Word(origin='test origin c', target='test target c')
        ])
        cls.test_topic.words.add(word_a)

    def test_search_for_words(self):
        filtered_path = reverse('filter_words') + "?search=test%20target&topic="
        response = self.client.get(filtered_path)
        self.assertContains(response, 'test target a')
        self.assertContains(response, 'test target b')
        self.assertContains(response, 'test target c')

    def test_search_for_word(self):
        filtered_path = reverse('filter_words') + "?search=test%20target%20a&topic="
        response = self.client.get(filtered_path)
        self.assertContains(response, 'test target a')
        self.assertNotContains(response, 'test target b')
        self.assertNotContains(response, 'test target c')

    def test_search_for_words_in_topic(self):
        filter_string = f'?search=&topic={self.test_topic.pk}'
        filtered_path = reverse('filter_words') + filter_string
        response = self.client.get(filtered_path)
        self.assertContains(response, 'test target a')
        self.assertNotContains(response, 'test target b')
        self.assertNotContains(response, 'test target c')

    def test_search_for_topicless_words(self):
        filtered_path = reverse('filter_words') + "?search=&topic=-1"
        response = self.client.get(filtered_path)
        self.assertNotContains(response, 'test target a')
        self.assertContains(response, 'test target b')
        self.assertContains(response, 'test target c')


class WordUpdateViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_topic = Topic.objects.create(name='Test Topic', long_desc='This is a test.')
        cls.word = Word.objects.create(origin='test origin a', target='test target a')
        cls.test_topic.words.add(cls.word)
        cls.path = reverse('word_update', args=[cls.word.pk])
        cls.view_class = WordUpdateView
        cls.template_path = 'editor/word_form.html'

    def test_page_contains_form(self):
        response = self.client.get(self.path)
        form = response.context.get('form')
        self.assertIsInstance(form, WordUpdateForm)

    def test_word_update_successful(self):
        self.client.post(self.path, {'origin': 'test origin a UPDATED', 'target': 'test target a UPDATED'})
        self.word.refresh_from_db()
        self.assertEquals(self.word.origin, 'test origin a UPDATED')
        self.assertEquals(self.word.target, 'test target a UPDATED')

    def test_redirect_after_updating_from_all_topics_page(self):
        response = self.client.post(self.path, {'origin': 'test origin a UPDATED', 'target': 'test target a UPDATED'},
                                    follow=True)
        self.assertRedirects(response, reverse('topic_words'), status_code=302)

    def test_redirect_after_deleting_from_single_topic_page(self):
        # when a user updates a Word having located it via a single Topic page, they are redirected there after update.
        session = self.client.session
        session['recent_topic'] = 1
        session.save()
        response = self.client.post(self.path, {'origin': 'test origin a UPDATED', 'target': 'test target a UPDATED'},
                                    follow=True)
        self.assertRedirects(response, reverse('topic_words', kwargs={'topic_id': 1}), status_code=302)


class TopicUpdateViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_topic = Topic.objects.create(name='Test Topic', long_desc='This is a test.')
        cls.path = reverse('topic_update', args=[cls.test_topic.pk])
        cls.view_class = TopicUpdateView
        cls.template_path = 'editor/topic_form.html'

    def test_page_contains_form(self):
        response = self.client.get(self.path)
        form = response.context.get('form')
        self.assertIsInstance(form, TopicForm)

    def test_topic_update_successful(self):
        self.client.post(self.path, {'name': 'Test Topic UPDATED', 'available_from': datetime.date.today(),
                                     'short_desc': 'sd'})
        self.test_topic.refresh_from_db()
        self.assertEquals(self.test_topic.name, 'Test Topic UPDATED')


class TopicDeleteViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_topic = Topic.objects.create(name='Test Topic', long_desc='This is a test.')
        cls.path = reverse('topic_delete', args=[cls.test_topic.pk])
        cls.view_class = TopicDeleteView
        cls.template_path = 'editor/topic_confirm_delete.html'

    def test_are_you_sure_page(self):
        response = self.client.get(self.path, follow=True)
        self.assertContains(response, 'Are you sure you want to')

    def test_actually_deleting_object(self):
        self.client.post(self.path, follow=True)
        self.assertFalse(Topic.objects.filter(name='Test Topic').exists())

    def test_redirect_after_deleting_object(self):
        response = self.client.post(self.path, follow=True)
        self.assertRedirects(response, reverse('home'), status_code=302)


class WordDeleteViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_topic = Topic.objects.create(name='Test Topic', long_desc='This is a test.')
        cls.word = Word.objects.create(origin='test origin a', target='test target a')
        cls.test_topic.words.add(cls.word)
        cls.path = reverse('word_delete', args=[cls.word.pk])
        cls.view_class = WordDeleteView
        cls.template_path = 'editor/word_confirm_delete.html'

    def test_are_you_sure_page(self):
        response = self.client.get(self.path, follow=True)
        self.assertContains(response, 'Are you sure you want to')

    def test_actually_deleting_object(self):
        self.client.post(self.path, follow=True)
        self.assertFalse(Word.objects.filter(origin='test origin a').exists())

    def test_redirect_after_deleting_from_all_topics_page(self):
        response = self.client.post(self.path, follow=True)
        self.assertRedirects(response, reverse('topic_words'), status_code=302)

    def test_redirect_after_deleting_from_single_topic_page(self):
        # when a user deletes a Word having located it via a single Topic page, they are redirected there after delete.
        session = self.client.session
        session['recent_topic'] = 1
        session.save()
        response = self.client.post(self.path, follow=True)
        self.assertRedirects(response, reverse('topic_words', kwargs={'topic_id': 1}), status_code=302)
