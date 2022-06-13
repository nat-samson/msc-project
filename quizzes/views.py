from django.http import HttpResponse
from django.shortcuts import render

# dummy data, will get data from model later
topics = [
    {
        'name': 'My Family',
        'words': {'Mother': 'die Mutter', 'Father': 'der Vater'}
    },
    {
        'name': 'Going On Holiday',
        'words': {'Vacation': 'der Urlaub', 'Beach': 'der Strand'}
    },
    {
        'name': 'Animals',
        'words': {'Dog': 'der Hund', 'Cat': 'die Katze'}
    }
]


# temporary basic home view
def home(request):
    context = [topic.get('name') for topic in topics]
    return HttpResponse('<br>'.join(context))
