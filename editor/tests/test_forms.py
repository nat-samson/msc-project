from unittest import SkipTest

from django.test import SimpleTestCase

from editor.forms import TopicForm, WordFilterForm, WordUpdateForm, WordCreateForm


class BaseTestCase(SimpleTestCase):
    def setUp(self):
        self.form = None
        self.expected_fields = None

        # Mark tests as abstract unless they are members of a BaseTestCase subclass
        if self.__class__ == BaseTestCase:
            raise SkipTest('Abstract test. Please ignore.')

    def test_form_fields(self):
        # tests the form before it is rendered. Rendered form is tested in test_views.py
        fields = tuple(self.form.fields.keys())
        self.assertEquals(fields, self.expected_fields)


class TopicFormTests(BaseTestCase):
    def setUp(self):
        self.form = TopicForm()
        self.expected_fields = ('name', 'long_desc', 'short_desc', 'available_from', 'is_hidden')


class WordCreateFormTests(SimpleTestCase):
    def setUp(self):
        self.form = WordCreateForm()
        self.expected_fields = ('origin', 'target')


class WordUpdateFormTests(SimpleTestCase):
    def setUp(self):
        self.form = WordUpdateForm()
        self.expected_fields = ('origin', 'target', 'topics')


class WordFilterFormTests(SimpleTestCase):
    def setUp(self):
        self.form = WordFilterForm()
        self.expected_fields = ('search', 'topic')
