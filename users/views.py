from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render


# Create your views here.
def register(request):
    form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
