import datetime
from datetime import date

from django.db import models

from users.models import User

MAX_SCORE = 5
QUIZ_INTERVALS = (0, 1, 3, 6, 10, 15)  # please note MAX_SCORE must be < len(QUIZ_INTERVALS)


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
    students = models.ManyToManyField(User, through='WordScore',
                                      through_fields=('word', 'student'), related_name='words')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('origin',)

    def __str__(self):
        return f'{self.origin} -> {self.target}'


class WordScore(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    consecutive_correct = models.PositiveSmallIntegerField(default=0)
    times_seen = models.PositiveSmallIntegerField(default=1)
    times_correct = models.PositiveSmallIntegerField(default=0)
    next_review = models.DateField(default=date.today)

    class Meta:
        unique_together = ('word', 'student')

    def __str__(self):
        return f'{self.student} / {self.word}: {self.score}'

    @property
    def score(self):
        # enforce a maximum score for each word
        return min(self.consecutive_correct, MAX_SCORE)

    def set_next_review(self):
        self.refresh_from_db()
        days_to_add = QUIZ_INTERVALS[self.score]
        self.next_review = datetime.date.today() + datetime.timedelta(days=days_to_add)


class QuizResults(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    incorrect_answers = models.PositiveSmallIntegerField(default=0)

    def get_points(self):
        return max(self.correct_answers * 10 - self.incorrect_answers * 2, 0)
