from datetime import datetime

from crispy_bulma.layout import Submit, Reset, FormGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from django import forms
from django.forms import DateInput
from django.urls import reverse_lazy

from quizzes.models import Topic
from users.models import User


class DashboardFilterForm(forms.Form):
    """ Custom form to enable teachers to filter the charts on the Dashboard by student and date range. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy('data-student-charts')
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

    # Specific field settings
    topics = forms.ModelChoiceField(
        queryset=Topic.objects.order_by('name'),
        required=False, empty_label="** All Topics **")
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_student=True, is_active=True).order_by('last_name'),
        required=False, empty_label="** All Students **")
    date_from = forms.DateField(
        label='Date From', required=False, widget=DateInput(attrs={'type': 'date', 'max': datetime.now().date()}))
    date_to = forms.DateField(
        label='Date To', required=False, widget=DateInput(attrs={'type': 'date', 'max': datetime.now().date()}))


class DatePresetFilterForm(forms.Form):
    """ Custom form to enable filtering by date range from a list of common presets. """
    def __init__(self, action, **kwargs):
        super().__init__(**kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy(action)
        self.helper.form_id = 'date-filter-form'
        self.helper.layout = Layout(
                Field('date_range'),
                Submit('submit', 'Submit', css_class='is-info', css_id='filter-submit')
        )

    # Specific field settings
    DATE_CHOICES = (
        (0, "Today"),
        (7, "Last 7 Days"),
        (30, "Last 30 Days"),
        (None, "All Time"),
    )
    date_range = forms.ChoiceField(choices=DATE_CHOICES, label="Set Date Range:", required=False)
