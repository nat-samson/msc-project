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
    """ Custom form to enable teachers to filter the charts on the Dashboard """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy('filter-chart')
        self.helper.form_id = 'filter-form'
        self.helper.form_horizontal = True
        self.helper.layout = Layout(
            Field('topics'),
            Field('students'),
            Field('date_from'),
            Field('date_to'),
            FormGroup(
                Reset('reset', 'Reset', css_class='is-light is-small'),
                Submit('submit', 'Update', css_class='is-success is-small', css_id='filter-submit'))
        )

    # settings for each field
    topics = forms.ModelChoiceField(
        queryset=Topic.objects.order_by('name'),
        required=False, empty_label="** All Topics **")
    students = forms.ModelChoiceField(
        queryset=User.objects.filter(is_student=True, is_active=True).order_by('last_name'),
        required=False, empty_label="** All Students **")
    date_from = forms.DateField(
        label='Date From', required=False, widget=DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(
        label='Date To', required=False, widget=DateInput(attrs={'type': 'date', 'max': datetime.now().date()}))


class DatePresetFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'date-filter-form'
        self.helper.layout = Layout(
            FormGroup(
                Field('date_range'),
                Submit('submit', 'Submit', css_class='is-success', css_id='filter-submit'),)
        )

    DATE_CHOICES = (
        (0, "Today"),
        (7, "Last 7 Days"),
        (30, "Last 30 Days"),
        (None, "All Time"),
    )
    date_range = forms.ChoiceField(choices=DATE_CHOICES, label="Date Range", required=False)
