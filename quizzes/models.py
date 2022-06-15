from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=100, blank=True)
    is_hidden = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # provides count of number of words in given topic
    def word_count(self):
        return self.words.count()


class Word(models.Model):
    origin = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='words')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('origin', 'topic'), ('target', 'topic')
        ordering = ('topic', 'origin',)

    def __str__(self):
        return f'{self.origin} -> {self.target}'
