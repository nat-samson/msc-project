from django.db.models import FilteredRelation, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, FormView

from quizzes.models import Topic, Word


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

        # get the current user's word scores for the given topic
        context['words_with_scores'] = Word.objects.filter(topics=context['topic']).annotate(
            score=FilteredRelation('wordscore', condition=Q(wordscore__student=self.request.user)),
        ).values('origin', 'target', 'score')

        return context


class QuizDataView(FormView):
    model = Topic
    template_name = 'quizzes/quiz.html'


def quiz_data(request, pk):
    # some function call here to get quiz data
    # quiz_data = getQuizData(pk, user)

    # dummy data for now
    data = {
        'questions': [
            {
                'word_id': 3,
                'target_to_origin': True,
                'question': 'Mouse',
                'correct_answer': 'Die Maus',
                'incorrect_answers': ['Der Bär', 'Der Hund', 'Die Katze']
            },
            {
                'word_id': 2,
                'target_to_origin': True,
                'question': 'Dog',
                'correct_answer': 'Der Hund',
                'incorrect_answers': ['Die Maus', 'Der Hund', 'Die Katze']
            },
            {
                'word_id': 1,
                'target_to_origin': False,
                'question': 'Die Katze',
                'correct_answer': 'Cat',
                'incorrect_answers': ['Dog', 'Bear', 'Mouse']
            }
        ]
    }
    return JsonResponse(data)


class QuizResultsView(TemplateView):
    pass
