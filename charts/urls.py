from django.urls import path
from .views import dashboard, chart_topic_points, chart_topic_quizzes, chart_topic_words

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('data/topic-points', chart_topic_points, name='data-topic-points'),
    path('data/topic-quizzes', chart_topic_quizzes, name='data-topic-quizzes'),
    path('data/topic-words', chart_topic_words, name='data-topic-words'),
]
