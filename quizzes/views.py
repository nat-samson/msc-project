from django.shortcuts import render
from django.views.generic import ListView

from quizzes.models import Topic


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
    ordering = ['-date_created']
    #paginate_by = 6  # TODO: Pagination
