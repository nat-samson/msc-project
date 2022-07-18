from django import template

register = template.Library()


@register.simple_tag(name='to_revise')
def count_of_words_to_revise(topic, user):
    # lets templates know the number of words that are due for revision (for given user & topic)
    return topic.words_due_revision(user).count()


@register.filter(name='is_due_revision', is_safe=True)
def is_due_revision(topic, user):
    # lets template know if a topic has words that are due for revision (for given user & topic)
    return topic.words_due_revision(user).exists()


@register.simple_tag(name='results_reaction')
def results_reaction(correct, total_qs):
    # enhance the quiz results page with a score-specific response
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
