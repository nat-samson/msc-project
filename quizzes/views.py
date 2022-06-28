import datetime

from django.db.models import FilteredRelation, Q, F
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView

from quizzes import quiz_builder
from quizzes.models import Topic, Word, WordScore, QuizResults


# temporary basic home view - INACTIVE
def home(request):
    context = {
        'topics': Topic.objects.all()
    }
    return render(request, 'quizzes/home.html', context)


class TopicListView(ListView):
    model = Topic
    template_name = 'quizzes/home.html'
    context_object_name = 'topics'
    ordering = ['date_created']
    #paginate_by = 6  # TODO: Pagination
    # TODO: only show topics that are 'quizzable', i.e. have enough words, aren't hidden


class TopicDetailView(DetailView):
    # model tells the view which model to use to create the detail view
    model = Topic
    fields = ['name', 'long_desc', 'short_desc']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the current user's word scores for the given topic (using an outer join with WordScore)
        context['words_with_scores'] = Word.objects.filter(topics=context['topic']).annotate(
            joinscore=FilteredRelation('wordscore', condition=Q(wordscore__student=self.request.user)),
        ).values_list('origin', 'target', 'joinscore__score')

        return context


def quiz(request, topic_pk):
    if request.method == 'POST':
        # TODO: processing the results of the quiz

        # get the quiz results data out of request.POST
        results = dict(request.POST.lists())
        results.pop('csrfmiddlewaretoken')

        correct = 0
        incorrect = 0

        # process the data
        for question, answer in results.items():
            # exclude unanswered questions
            if len(answer) == 2:
                if answer[0] == answer[1]:  # correct
                    correct += 1
                    WordScore.objects.update_or_create(word_id=question, student=request.user,
                                                       consecutive_correct=F('consecutive_correct') + 1,
                                                       times_seen=F('times_seen') + 1,
                                                       next_review=datetime.date.today() + datetime.timedelta(days=1),
                                                       score=F('score') + 1)
                else:  # incorrect
                    incorrect += 1
                    WordScore.objects.update_or_create(word_id=question, student=request.user,
                                                       consecutive_correct=0, times_seen=F('times_seen') + 1,
                                                       next_review=datetime.date.today() + datetime.timedelta(days=1),
                                                       score=F('score') - 1)

        # store results of quiz
        QuizResults.objects.create(student=request.user, topic_id=topic_pk, correct_answers=correct, incorrect_answers=incorrect)

        # redirect user to results page (currently using home as placeholder)
        return redirect('home')
    else:
        # get the data needed to build the form in the template
        # pass it to a view
        questions = quiz_builder.get_quiz(request.user, topic_pk)

        return render(request, 'quizzes/quiz.html', {'questions': questions})


class QuizResultsView(TemplateView):
    pass
