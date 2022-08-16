from crispy_bulma.layout import Submit, Reset, FormGroup, Row, Column
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms

from django.forms import DateInput, ModelForm, Textarea
from django.urls import reverse_lazy
from emoji_picker.widgets import EmojiPickerTextInput

from quizzes.models import Topic, Word


class CustomMultiChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, topic):
        # nicer styling for checkboxes
        return topic.name


class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'long_desc', 'short_desc', 'available_from', 'is_hidden']
        widgets = {
            'short_desc': EmojiPickerTextInput(attrs={'size': 10, 'style': 'font-size: xx-large'}),
            'long_desc': Textarea(attrs={'rows': 3, 'cols': 20}),
            'available_from': DateInput(attrs={'type': 'date'}),
        }

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Save', css_class='is-success has-text-weight-semibold'))


class WordForm(ModelForm):
    class Meta:
        model = Word
        fields = ['origin', 'target']

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_action = reverse_lazy('add_word')
    helper.form_class = 'word-create-form'
    helper.layout = Layout(
        Field('origin'),
        Field('target'),
        FormGroup(
            Reset('reset', 'Cancel', css_class='is-outlined has-text-weight-semibold', css_id='cancel-button'),
            Submit('submit', 'Save', css_class='is-success has-text-weight-semibold'))
    )


class WordUpdateForm(ModelForm):
    class Meta:
        model = Word
        fields = ['origin', 'target', 'topics']

    topics = CustomMultiChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    helper = FormHelper()
    helper.layout = Layout(
        Field('origin'),
        Field('target'),
        Field('topics'),
        FormGroup(
            Submit('submit', 'Update', css_class='is-success has-text-weight-semibold')),
    )


class WordFilterForm(forms.Form):
    helper = FormHelper()
    helper.form_method = 'GET'
    helper.form_action = reverse_lazy('filter_words')
    helper.form_id = 'word-filter-form'
    helper.form_show_labels = False
    helper.layout = Layout(
        Row(
            Column(Field('search')),
            Column(Field('topic'))),
        FormGroup(
            Reset('reset', 'Reset', css_class='is-outlined', css_id='filter-reset'),
            Submit('submit', 'Submit', css_class='is-success has-text-weight-semibold', css_id='filter-submit')))

    # Individual field settings
    search = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'placeholder': 'Search by Target or Origin'}))
    topic = forms.ChoiceField(required=False,
                              choices=[('', '** All Topics **'), (-1, '** No Topics **')] +
                                      list(Topic.objects.order_by('name').values_list('pk', 'name')))
