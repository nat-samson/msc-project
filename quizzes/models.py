import datetime

from django.db import models
from django.db.models import F, Count

from users.models import User

QUIZ_INTERVALS = (1, 3, 7, 13, 21, 30)
MAX_SCORE = len(QUIZ_INTERVALS)


class Topic(models.Model):
    """A Django model representing a 'Topic', that is, a thematic grouping of Words.

    Topics can be further illustrated using descriptions, and can be controlled.
    """

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

    def words_due_revision(self, user, today=datetime.date.today()):
        """Returns a queryset containing this Topic's Words due for revision today (or on specified date)."""
        words_in_topic = Word.objects.filter(topics=self)
        words_not_due = Word.objects.filter(topics=self, wordscore__next_review__gt=today, wordscore__student=user)

        # words due revision = all words in given topic - words NOT due revision by given user
        return words_in_topic.difference(words_not_due)

    @staticmethod
    def all_topics_words_due_revision(user, today=datetime.date.today()):
        """Returns a queryset containing all Words across all Topics due for revision today (or on specified date)."""
        # word must part of a live topic to be counted
        all_words = Word.objects.filter(topics__in=Topic.live_topics().values_list('id'))
        words_not_due = all_words.filter(wordscore__next_review__gt=today, wordscore__student=user)
        return all_words.difference(words_not_due)

    @staticmethod
    def live_topics(today=datetime.date.today()):
        """Returns a queryset containing all live Topics, i.e. those with >= 4 Words, not future dated, not hidden."""
        return Topic.objects.annotate(word_count=Count('words')).filter(word_count__gte=4,
                                                                        available_from__lte=today, is_hidden=False)


class Word(models.Model):
    """A Django model representing a Word, the items that the User is attempting to memorise.

    Each Word is formed of a definition in its 'origin' (known) and 'target' (unknown) language.
    Each Word can belong to multiple (or 0) Topics.
    Each Word is related to students (i.e. Users) via a WordScore object.
    """

    origin = models.CharField(max_length=100, unique=True)
    target = models.CharField(max_length=100, unique=True)
    topics = models.ManyToManyField(Topic, related_name='words', blank=True)
    students = models.ManyToManyField(User, through='WordScore',
                                      through_fields=('word', 'student'), related_name='words')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.origin} -> {self.target}'


class WordScore(models.Model):
    """A Django model representing a particular User's score for a particular Word.

    This model is the basis of the application's spaced repetition scheduling algorithm, tracking key data points
    to estimate a User's current familiarity with a Word.
    """

    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    consecutive_correct = models.PositiveIntegerField(default=0)
    times_seen = models.PositiveIntegerField(default=1)
    times_correct = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    next_review = models.DateField(default=datetime.date.today)

    class Meta:
        unique_together = ('word', 'student')

    def __str__(self):
        return f'{self.student} / {self.word}: {self.score()}'

    def score(self):
        """ Enforce a maximum score for each word. """
        return min(self.consecutive_correct, MAX_SCORE)

    def set_next_review(self, today=datetime.date.today()):
        """Updates the next_review field with the appropriate date based on the current Score."""
        days_to_add = QUIZ_INTERVALS[self.score()]
        self.next_review = today + datetime.timedelta(days=days_to_add)


class QuizResults(models.Model):
    """A Django model representing the results of a Quiz.

     An entry is generated at the end of each Quiz, summarising the results and the number of points earned by the User.
     """

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date_created = models.DateField(default=datetime.date.today)
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Quiz Results: {self.student.get_full_name()} / {self.topic} on {self.date_created}"

    @staticmethod
    def update_user_streak(student, today=datetime.date.today()):
        """Updates user's streak if this is their first quiz taken today."""
        yesterday = today - datetime.timedelta(1)
        quizzes_since_yesterday = QuizResults.objects.filter(
            student=student, date_created__gte=yesterday).values_list('date_created', flat=True)

        if today not in quizzes_since_yesterday:
            if yesterday in quizzes_since_yesterday:
                # student is continuing an existing streak
                student.streak = F('streak') + 1
            else:
                # student is starting a new streak
                student.streak = 1
            student.save(update_fields=['streak'])

    @staticmethod
    def get_user_streak(student):
        """Gets the user's current streak as of now. (User.streak stores the streak as of its latest update)."""
        yesterday = datetime.date.today() - datetime.timedelta(1)
        if QuizResults.objects.filter(student=student, date_created__gte=yesterday).exists():
            streak = student.streak
        else:
            streak = 0
        return streak
