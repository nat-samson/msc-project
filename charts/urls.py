from django.urls import path
from .views import progress, chart_topic_points, chart_topic_quizzes, chart_topic_words, get_filtered_data_student, \
    chart_points_per_day, dashboard, get_student_charts_data, get_filtered_data_teacher

urlpatterns = [
    path('progress/', progress, name='progress'),
    path('dashboard/', dashboard, name='dashboard'),
    path('api/topic-points/', chart_topic_points, name='data-topic-points'),
    path('api/topic-quizzes/', chart_topic_quizzes, name='data-topic-quizzes'),
    path('api/points-day/', chart_points_per_day, name='data-points-day'),
    path('api/filter-dates-student/', get_filtered_data_student, name='filter-date-student'),
    path('api/filter-dates-teacher/', get_filtered_data_teacher, name='filter-date-teacher'),
    path('api/topic-words/', chart_topic_words, name='data-topic-words'),
    path('api/student-charts/', get_student_charts_data, name='data-student-charts'),
]
