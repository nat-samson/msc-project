from django.urls import path
from .views import progress, get_filtered_data_student, dashboard, get_updatable_charts, \
    get_filtered_data_teacher, get_points_per_day

urlpatterns = [
    path('progress/', progress, name='progress'),
    path('dashboard/', dashboard, name='dashboard'),
    path('api/filter-date-student/', get_filtered_data_student, name='filter-date-student'),
    path('api/filter-date-teacher/', get_filtered_data_teacher, name='filter-date-teacher'),
    path('api/updatable-charts/', get_updatable_charts, name='data-updatable-charts'),
    path('api/points-per-day/', get_points_per_day, name='data-points-per-day'),
]
