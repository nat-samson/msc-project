from django.urls import path
from .views import HomeView, TopicDetailView, QuizView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('quiz/<int:topic_id>/', QuizView.as_view(), name='quiz'),
]
