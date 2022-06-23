from django.db.models import FilteredRelation, Q
from django.shortcuts import render
from django.views.generic import ListView, DetailView

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
