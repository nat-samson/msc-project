from datetime import datetime

from crispy_bulma.layout import Submit, Reset, FormGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.forms import DateInput
from django.urls import reverse_lazy

from quizzes.models import Topic
from users.models import User


class BaseFilterForm(forms.Form):
    """Template for designing new forms used to filter Dashboard/Progress template data."""
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy(url)

    # Individual field settings
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.order_by('name'),
        required=False, empty_label="** All Topics **")
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_teacher=False, is_active=True).order_by('last_name'),
        required=False, empty_label="** All Students **")

    # Including two options for setting date range: Either via presets, or custom to/from
    DATE_CHOICES = (
        (0, "Today"),
        (7, "Last 7 Days"),
        (30, "Last 30 Days"),
        (None, "All Time"),
    )
    date_range = forms.ChoiceField(choices=DATE_CHOICES, label="Set Date Range:", required=False)
    date_to = forms.DateField(
        label='Date To', required=False, widget=DateInput(attrs={'type': 'date', 'max': datetime.now().date()}))
    date_from = forms.DateField(
        label='Date From', required=False, widget=DateInput(attrs={'type': 'date', 'max': datetime.now().date()}))


class DateFilterForm(BaseFilterForm):
    """Custom form to enable filtering by date range from a list of common presets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = 'date-filter-form'
        self.helper.layout = Layout(
                Field('date_range'),
                Submit('submit', 'Submit', css_class='is-info', css_id='filter-submit')
        )


class StudentDateFilterForm(BaseFilterForm):
    """Custom form to enable teachers to filter the charts on the Dashboard by student and date range."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = 'student-filter-form'
        self.helper.form_horizontal = True
        self.helper.layout = Layout(
            Field('student'),
            Field('date_from'),
            Field('date_to'),
            FormGroup(
                Reset('reset', 'Reset', css_class='is-outlined'),
                Submit('submit', 'Update', css_class='is-success', css_id='student-filter-submit'))
        )


class TopicDateFilterForm(BaseFilterForm):
    """Custom form to enable teachers to filter the charts on the Dashboard by topic and date range."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = 'topic-filter-form'
        self.helper.form_horizontal = True
        self.helper.layout = Layout(
            Field('topic'),
            Field('date_range'),
            FormGroup(
                Reset('reset', 'Reset', css_class='is-outlined'),
                Submit('submit', 'Update', css_class='is-success', css_id='topic-filter-submit'))
        )
