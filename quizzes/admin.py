from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import Topic, Word

# Register your models here.


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_hidden', 'link_to_words',)
    fields = ('name', 'description', 'is_hidden',)
    search_fields = ('name',)

    def link_to_words(self, obj):
        count = obj.words.count()
        url = (
                reverse('admin:quizzes_word_changelist')
                + '?' + urlencode({'topics__id': f'{obj.id}'})
        )
        # extra formatting handles correct pluralisation
        return format_html('<a href="{}">{} Word{}</a>', url, count, 's'[:count != 1])

    link_to_words.short_description = 'Words'


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('origin', 'target', 'get_topics_list_str',)
    list_filter = ('topics',)
    fields = ('origin', 'target', 'topics',)
    search_fields = ('origin', 'target',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('topics')

    def get_topics_list_str(self, obj):
        return ', '.join([x.name for x in obj.topics.all()])

    get_topics_list_str.short_description = 'Topics List'
