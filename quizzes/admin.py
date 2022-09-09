from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import Topic, Word


class TopicWordsInline(admin.TabularInline):
    model = Word.topics.through
    extra = 0
    ordering = ('word__origin',)
    autocomplete_fields = ('word',)
    verbose_name = "Word registered to this topic"
    verbose_name_plural = "Words registered to this topic"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('word')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_hidden', 'available_from', 'link_to_words',)
    fields = ('name', 'short_desc', 'long_desc', 'is_hidden', 'available_from',)
    search_fields = ('name', 'long_desc', 'words__origin', 'words__target')
    search_help_text = "Search by Name, Long Description, or by word within a Topic..."
    list_editable = ('is_hidden', 'available_from',)
    ordering = ('date_created', 'available_from',)
    inlines = [TopicWordsInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('words')

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
    list_display = ('id', 'origin', 'target', 'get_topics_list_str',)
    list_filter = ('topics',)
    fields = ('origin', 'target', 'topics',)
    search_fields = ('origin', 'target', 'topics__name')
    search_help_text = "Search by Origin, Target, Topic..."
    list_editable = ('origin', 'target',)
    list_display_links = ('id', 'get_topics_list_str',)
    ordering = ('date_created',)

    # displays Topics using a horizontal filter (rather than checkboxes)
    filter_horizontal = ('topics',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('topics')

    def get_topics_list_str(self, word):
        topics = word.topics.all()
        if topics.exists():
            return ', '.join([x.name for x in topics])
        else:
            return '** No Topics **'

    get_topics_list_str.short_description = 'Topics List'
