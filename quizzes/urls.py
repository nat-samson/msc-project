from django.urls import path
from .views import TopicListView, TopicDetailView, quiz

urlpatterns = [
    path('', TopicListView.as_view(), name='home'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('topic/<int:pk>/quiz/', quiz, name='quiz'),
]
