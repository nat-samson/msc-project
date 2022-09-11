from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse

register = template.Library()


@register.simple_tag(name='to_revise')
def count_of_words_to_revise(topic, user):
    """Template tag for getting the number of words that are due for revision (for given user & topic)."""
    return topic.words_due_revision(user).count()


@register.simple_tag(name='results_reaction')
def results_reaction(correct, total_qs):
    """Template tag for getting a string message that congratulates the user after a quiz."""
    try:
        score = int(correct) / int(total_qs)
        if score >= 0.8:
            return "Congratulations! ", "🏆"
        elif score >= 0.5:
            return "Nicely done. ", "😎"
        else:
            return "Keep at it! ", "📚"
    except (ZeroDivisionError, ValueError):
        return "Divide by zero error! ", "❓"


@register.filter(name='get_filtered_list_url')
@stringfilter
def get_filtered_list_url(topic_id):
    """Template tag for getting the appropriate URL direct to the Topic page in Django admin."""
    url = reverse("admin:quizzes_word_changelist") + "?topics__id__exact=" + topic_id
    return url
