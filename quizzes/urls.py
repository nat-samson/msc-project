from django.urls import path
from . import views
from .views import TopicListView

urlpatterns = [
    path('', TopicListView.as_view(), name='home'),
]
