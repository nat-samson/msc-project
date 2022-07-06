import datetime

from django.db import models
from django.utils.functional import cached_property

from users.models import User

MAX_SCORE = 5
QUIZ_INTERVALS = (1, 3, 7, 13, 21, 30)  # please note MAX_SCORE must be < len(QUIZ_INTERVALS)


class Topic(models.Model):
    name = models.CharField(max_length=32, unique=True)
    long_desc = models.CharField(max_length=255, blank=True)
    short_desc = models.CharField(max_length=10, default='❓🧠❓')
    is_hidden = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def words_due_revision(self, user):
        # words due revision = all words in given topic - those words NOT due revision by given user
        today = datetime.date.today()
        words_in_topic = Word.objects.filter(topics=self).order_by()
        words_not_due = Word.objects.filter(topics=self, wordscore__next_review__gt=today, wordscore__student=user).order_by()

        return words_in_topic.difference(words_not_due)

    @staticmethod
    def all_topics_words_due_revision(user):
        today = datetime.date.today()
        all_words = Word.objects.all()
        words_not_due = Word.objects.filter(wordscore__next_review__gt=today, wordscore__student=user).order_by()

        return all_words.difference(words_not_due)


class Word(models.Model):
    origin = models.CharField(max_length=100, unique=True)
    target = models.CharField(max_length=100, unique=True)
    topics = models.ManyToManyField(Topic, related_name='words')
    students = models.ManyToManyField(User, through='WordScore',
                                      through_fields=('word', 'student'), related_name='words')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.origin} -> {self.target}'


class WordScore(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    consecutive_correct = models.PositiveSmallIntegerField(default=0)
    times_seen = models.PositiveSmallIntegerField(default=1)
    times_correct = models.PositiveSmallIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    next_review = models.DateField(default=datetime.date.today)

    class Meta:
        unique_together = ('word', 'student')

    def __str__(self):
        return f'{self.student} / {self.word}: {self.score}'

    @cached_property
    def score(self):
        # enforce a maximum score for each word
        return min(self.consecutive_correct, MAX_SCORE)

    def set_next_review(self):
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
