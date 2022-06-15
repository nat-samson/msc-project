from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import Topic, Word

# Register your models here.


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'word_count', 'is_hidden', 'link_to_words',)
    fields = ('name', 'description', 'is_hidden',)

    def link_to_words(self, obj):
        count = obj.word_count()
        url = (
                reverse("admin:quizzes_word_changelist")
                + "?" + urlencode({"topic__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Words</a>', url, count)

    link_to_words.short_description = 'Words'


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('origin', 'target', 'topic',)
    list_filter = ('topic',)
    search_fields = ('origin', 'target',)
    fields = ('origin', 'target', 'topic',)
