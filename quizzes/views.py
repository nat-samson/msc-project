from django.shortcuts import render
from quizzes.models import Topic


# temporary basic home view
def home(request):
    context = {
        'topics': Topic.objects.all()
    }
    return render(request, 'quizzes/home.html', context)
