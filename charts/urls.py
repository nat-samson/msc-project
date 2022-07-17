from django.urls import path
from .views import progress, chart_topic_points, chart_topic_quizzes, chart_topic_words, get_filtered_data_student

urlpatterns = [
    path('', progress, name='progress'),
    path('data/topic-points/', chart_topic_points, name='data-topic-points'),
    path('data/topic-quizzes/', chart_topic_quizzes, name='data-topic-quizzes'),
    path('data/topic-words/', chart_topic_words, name='data-topic-words'),
    path('data/filter-dates/', get_filtered_data_student, name='filter-date'),
]
