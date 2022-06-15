from django.contrib import admin
from .models import Topic, Word

# Register your models here.


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_hidden',)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('origin', 'target', 'topic',)
    list_filter = ('topic',)
    search_fields = ('origin', 'target',)
    fields = ('origin', 'target', 'topic',)
