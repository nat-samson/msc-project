import datetime
import random
from random import randint

from django.core.management import BaseCommand
from django.db.models import Count

from quizzes.models import Topic
from quizzes.quiz_builder import MAX_QUIZ_LENGTH
from quizzes.views import process_results
from users.models import User


MAX_QUIZZES_PER_DAY = 10


class Command(BaseCommand):
    """
    Terminal command for generating the specified days worth of quiz results data.
    """
    help = 'Generate x days worth of quiz results data for all active students.'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int, help='Indicates the number of days of quiz results to generate.')

    def handle(self, *args, **kwargs):
        days_to_generate = kwargs['days']
        today = datetime.date.today()

        # Only active students are used to generate data (Teachers are also excluded)
        students = User.objects.filter(is_teacher=False, is_active=True)

        # counters for printing in terminal after execution
        student_count = 0
        quiz_count = 0

        for student in students:
            student_count += 1
            quiz_date = today - datetime.timedelta(days_to_generate)

            while quiz_date <= today:
                # randomly decide how many quizzes to do today, and in which topics
                quizzes_today = get_quiz_today_count()

                topic_list = list(Topic.objects.annotate(word_count=Count('words'))
                                  .filter(is_hidden=False, word_count__gte=4))
                topics_to_quiz = random.choices(topic_list, k=quizzes_today)

                for topic in topics_to_quiz:
                    # do the quizzes!
                    words_to_quiz = topic.words_due_revision(student, quiz_date)[:MAX_QUIZ_LENGTH]
                    results = {word.id: correct_or_incorrect() for word in words_to_quiz}

                    if results:
                        process_results(results, student, topic.id, quiz_date)
                        quiz_count += 1

                quiz_date += datetime.timedelta(1)

        print(f"{student_count} students took {quiz_count} quizzes covering {days_to_generate} days.")


def get_quiz_today_count():
    """ Helper method to provide a more natural randomised count of quizzes to be taken 'today'."""
    quiz_count = -1
    keep_quizzing = True
    quiz_pc = 90
    pc_decay = 5  # after each quiz, it becomes slightly less likely the student will do another.

    while keep_quizzing and quiz_count <= MAX_QUIZZES_PER_DAY:
        quiz_count += 1
        keep_quizzing = randint(1, 100) <= quiz_pc
        quiz_pc -= pc_decay
    return quiz_count


def correct_or_incorrect():
    """ Helper method to provide a boolean that is 60% likely to be True """
    pc_accurate = 60
    return random.randint(1, 100) <= pc_accurate
