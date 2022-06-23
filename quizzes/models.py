from datetime import date

from django.db import models

from users.models import User


class Topic(models.Model):
    name = models.CharField(max_length=32, unique=True)
    long_desc = models.CharField(max_length=255, blank=True)
    short_desc = models.CharField(max_length=10, default='❓🧠❓')
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
    students = models.ManyToManyField(User, through='WordScore', through_fields=('word', 'student'), related_name='words')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('origin',)

    def __str__(self):
        return f'{self.origin} -> {self.target}'


class WordScore(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    consecutive_correct = models.PositiveSmallIntegerField(default=0)
    times_seen = models.PositiveSmallIntegerField(default=0)
    times_correct = models.PositiveSmallIntegerField(default=0)
    next_review = models.DateField(default=date.today)
    score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('word', 'student')


class QuizResults(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    incorrect_answers = models.PositiveSmallIntegerField(default=0)

    def get_points(self):
        return max(self.correct_answers * 10 - self.incorrect_answers * 2, 0)
