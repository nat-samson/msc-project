from django.urls import path
from .views import progress, chart_topic_points, chart_topic_quizzes, chart_topic_words, class_dashboard, \
    get_filtered_chart_data

urlpatterns = [
    path('', progress, name='progress'),
    path('class/', class_dashboard, name='dashboard'),
    path('data/topic-points/', chart_topic_points, name='data-topic-points'),
    path('data/topic-quizzes/', chart_topic_quizzes, name='data-topic-quizzes'),
    path('data/topic-words/', chart_topic_words, name='data-topic-words'),
    path('data/filter-chart/', get_filtered_chart_data, name='filter-chart'),
]
