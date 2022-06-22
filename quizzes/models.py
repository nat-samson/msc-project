from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=100, blank=True)
    is_hidden = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    """# provides count of number of words in given topic
    def word_count(self):
        return self.words.count()"""


class Word(models.Model):
    origin = models.CharField(max_length=100, unique=True)
    target = models.CharField(max_length=100, unique=True)
    topics = models.ManyToManyField(Topic, related_name='words')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('origin',)

    def __str__(self):
        return f'{self.origin} -> {self.target}'
