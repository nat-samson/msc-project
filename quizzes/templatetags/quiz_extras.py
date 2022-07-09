from django import template

register = template.Library()


@register.filter(name='to_revise')
def count_of_words_to_revise(topic, user):
    # lets templates know the number of words that are due for revision (for given user & topic)
    return topic.words_due_revision(user).count()


@register.filter(name='is_due_revision')
def is_due_revision(topic, user):
    # lets template know if a topic has words that are due for revision (for given user & topic)
    return topic.words_due_revision(user).exists()
