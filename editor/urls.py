from django.urls import path
from .views import TopicCreateView, TopicWordsView, add_word, WordUpdateView, TopicUpdateView, TopicDeleteView, \
    WordDeleteView, get_filtered_words

urlpatterns = [
    path('topic/create/', TopicCreateView.as_view(), name='topic_create'),
    path('topic/update/<pk>/', TopicUpdateView.as_view(), name='topic_update'),
    path('topic/delete/<pk>/', TopicDeleteView.as_view(), name='topic_delete'),
    path('topic/words/', TopicWordsView.as_view(), name='topic_words'),
    path('topic/words/<int:topic_id>/', TopicWordsView.as_view(), name='topic_words'),
    path('topic/add-word/', add_word, name='add_word'),
    path('topic/add-word/<int:topic_id>/', add_word, name='add_word'),
    path('topic/filter-words/', get_filtered_words, name='filter_words'),
    path('word/update/<pk>/', WordUpdateView.as_view(), name='word_update'),
    path('word/delete/<pk>/', WordDeleteView.as_view(), name='word_delete'),
]
