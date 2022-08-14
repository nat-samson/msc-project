from django.urls import path
from .views import HomeView, TopicDetailView, QuizView, TopicCreateView, TopicWordsView, add_word, WordUpdateView, \
    TopicUpdateView, TopicDeleteView, WordDeleteView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('topic/create/', TopicCreateView.as_view(), name='topic_create'),
    path('topic/update/<pk>/', TopicUpdateView.as_view(), name='topic_update'),
    path('topic/delete/<pk>/', TopicDeleteView.as_view(), name='topic_delete'),
    path('topic/words/', TopicWordsView.as_view(), name='topic_words'),
    path('topic/words/<int:topic_id>/', TopicWordsView.as_view(), name='topic_words'),
    path('topic/add-word/', add_word, name='add_word'),
    path('topic/add-word/<int:topic_id>/', add_word, name='add_word'),
    path('word/update/<pk>/', WordUpdateView.as_view(), name='word_update'),
    path('word/delete/<pk>/', WordDeleteView.as_view(), name='word_delete'),
    path('quiz/<int:topic_id>/', QuizView.as_view(), name='quiz'),
]
