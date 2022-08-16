import datetime

from django.db import models
from django.db.models import F

from users.models import User

QUIZ_INTERVALS = (1, 3, 7, 13, 21, 30)
MAX_SCORE = len(QUIZ_INTERVALS)


class Topic(models.Model):
    name = models.CharField(max_length=32, unique=True)
    long_desc = models.CharField(max_length=255, blank=True, verbose_name="Long Description")
    short_desc = models.CharField(max_length=10, default='❓🧠❓', verbose_name="Emoji Description",
                                  help_text="Illustrate the Topic with a few emoji. "
                                            "On Mac? Press CTRL+CMD+Space. On Windows? Press Windows key + fullstop.")
    is_hidden = models.BooleanField(default=False, verbose_name="Hide Topic",
                                    help_text="Hide the Topic from view. No quizzes can be taken "
                                              "using this Topic while it is hidden. "
                                              "Topics which contain fewer than four words are hidden regardless.")
    available_from = models.DateField(default=datetime.date.today)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def words_due_revision(self, user):
        # words due revision = all words in given topic - those words NOT due revision by given user
        today = datetime.date.today()
        words_in_topic = Word.objects.filter(topics=self)
        words_not_due = Word.objects.filter(topics=self, wordscore__next_review__gt=today, wordscore__student=user)
        return words_in_topic.difference(words_not_due)

    @staticmethod
    def all_topics_words_due_revision(user):
        # word must part of a visible topic to be counted
        today = datetime.date.today()

        all_words = Word.objects.filter(topics__is_hidden=False)
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
        return f'{self.student} / {self.word}: {self.score()}'

    def score(self):
        # enforce a maximum score for each word
        return min(self.consecutive_correct, MAX_SCORE)

    def set_next_review(self):
        days_to_add = QUIZ_INTERVALS[self.score()]
        self.next_review = datetime.date.today() + datetime.timedelta(days=days_to_add)


class QuizResults(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    incorrect_answers = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Quiz Results: {self.student.get_full_name()} / {self.topic} on {self.date_created}"

    @staticmethod
    def update_user_streak(student):
        """ Updates user's streak if this is their first quiz taken today. """
        today = datetime.date.today()
        if not QuizResults.objects.filter(student=student, date_created=today).exists():
            if QuizResults.objects.filter(student=student, date_created=today - datetime.timedelta(1)).exists():
                # student is continuing an existing streak
                student.streak = F('streak') + 1
            else:
                # student is starting a new streak
                student.streak = 1
            student.save(update_fields=['streak'])

    @staticmethod
    def get_user_streak(student):
        """ Gets the user's current streak as of now. (User.streak stores the streak as of its latest update).  """
        yesterday = datetime.date.today() - datetime.timedelta(1)
        if QuizResults.objects.filter(student=student, date_created__gte=yesterday).exists():
            streak = student.streak
        else:
            streak = 0
        return streak
