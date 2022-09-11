"""This module defines the specific queries required by the Charts Views."""

import datetime

from django.db.models import Sum, Count, CharField, Value
from django.db.models.functions import Concat

from charts.utils.chart_tools import prepare_data
from quizzes.models import QuizResults, WordScore
from users.models import User

PTS_PER_DAY_DATERANGE = 14  # number of days to display on Progress template linechart
MAX_WEAKEST_WORDS = 10  # maximum number of the weakest words to display
MAX_STREAKS = 3  # maximum number of students to display in the longest streaks table


def get_filtered_queryset(request):
    """Get the base QuizResults queryset for the data visualisations, applying the desired GET URL parameters."""
    qs = QuizResults.objects.filter(student__is_teacher=False)

    # extract filter settings from GET request, apply to queryset
    topic = request.GET.get('topic', None)
    date_range = request.GET.get('date_range', None)
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)

    # only teachers can filter by student. Students can only see their own data.
    if request.user.is_teacher:
        filter_student = request.GET.get('student', None)
        if filter_student:
            qs = qs.filter(student_id=filter_student)
    else:
        qs = qs.filter(student_id=request.user.id)

    # apply filters available to students and teachers
    if topic:
        qs = qs.filter(topic_id=topic)
    if date_range:
        from_date = datetime.date.today() - datetime.timedelta(int(date_range))
        qs = qs.filter(date_created__gte=from_date)
    if date_from:
        qs = qs.filter(date_created__gte=date_from)
    if date_to:
        qs = qs.filter(date_created__lte=date_to)

    return qs


def get_updatable_charts_data(qs):
    """Get the data required for the updatable charts data based on the filtered Queryset."""
    if not qs.exists():
        return {'points_per_topic': [], 'quizzes_per_topic': []}

    points_per_topic_data = _get_points_per_topic_data(qs)
    quizzes_per_topic_data = _get_quizzes_per_topic_data(qs)

    return {'points_per_topic': points_per_topic_data, 'quizzes_per_topic': quizzes_per_topic_data}


def _get_points_per_topic_data(qs):
    """Helper function that actually performs the Points Per Topic query, packages it up with labels."""
    points_per_topic = qs.values('topic__name').annotate(Sum('points')).values_list("topic__name", "points__sum")
    label = "Points"
    return prepare_data(points_per_topic, label)


def _get_quizzes_per_topic_data(qs):
    """Helper function that actually performs the Quizzes Per Topic query, packages it up with labels."""
    quizzes_per_topic = qs.values('topic__name').annotate(quizzes_taken=Count('id'))\
        .values_list("topic__name", "quizzes_taken")
    label = "Quizzes"
    return prepare_data(quizzes_per_topic, label)


def get_weakest_words_data(student=False):
    """Get a list of the Words with the worst % incorrect attempts, either for individual student or whole class."""
    scores = WordScore.objects.all()
    if student:
        scores = WordScore.objects.filter(student=student)

    weakest_words = list(scores.values('word').annotate(incorrect_pc=Sum('times_correct')*100/Sum('times_seen'))
                         .order_by('incorrect_pc')
                         .values_list('word__origin', 'word__target', 'incorrect_pc')[:MAX_WEAKEST_WORDS])

    # Top up the data so there are enough rows to fill the intended table
    while len(weakest_words) < MAX_WEAKEST_WORDS:
        weakest_words.append(("N/A", "N/A", "N/A"))

    return weakest_words


def get_student_streaks_data():
    """Get a list of the students with the longest streaks."""
    yesterday = datetime.date.today() - datetime.timedelta(1)

    # concatenates first and last names within the query itself
    streaks = list(QuizResults.objects.filter(student__is_teacher=False, date_created__gte=yesterday)
                   .annotate(
        full_name=Concat('student__first_name', Value(' '), 'student__last_name', output_field=CharField()))
                   .values('student', 'full_name', 'student__streak').distinct()
                   .values_list('full_name', 'student__streak')
                   .order_by('-student__streak')[:MAX_STREAKS])
    return streaks


def get_points_per_day_data(student):
    """Helper function that actually performs the Points Per Day query, packages it up with labels."""
    today = datetime.date.today()
    date_from = today - datetime.timedelta(PTS_PER_DAY_DATERANGE)
    student_results = QuizResults.objects.filter(student=student, date_created__gte=date_from)
    points_per_day = list(student_results.values('date_created').annotate(total_points=Sum('points'))
                          .order_by('date_created').values_list('date_created', 'total_points'))

    # fill in missing days
    if len(points_per_day) < PTS_PER_DAY_DATERANGE:
        dates_present = [data_point[0] for data_point in points_per_day]
        for day in range(PTS_PER_DAY_DATERANGE):
            date = date_from + datetime.timedelta(day)
            if date not in dates_present:
                points_per_day.insert(day, (date, 0))

    # line charts look better with same colour nodes
    colours = ['rgba(75, 192, 192, 1)', 'rgba(75, 192, 192, 1)']
    label = "Points"

    return prepare_data(points_per_day, label, colours)


def get_points_per_student_data(qs):
    """Helper function that actually performs the Points Per Student Per Topic query, packages it up with labels."""
    # only includes students who have completed a quiz within date range
    present_student_data = list(qs.values('student')
                                .annotate(total=Sum('points'),
                                          full_name=Concat('student__first_name', Value(' '), 'student__last_name'))
                                .values_list('full_name', 'total')
                                .order_by('-total', 'student__last_name'))

    # get students who have no quiz data
    missing_student_data = list(User.objects.filter(is_teacher=False)
                                .exclude(quizresults__in=qs)
                                .annotate(full_name=Concat('first_name', Value(' '), 'last_name'), total=Value(0))
                                .values_list('full_name', 'total')
                                .order_by('last_name'))

    final_data = present_student_data + missing_student_data

    if final_data:
        return final_data
    else:
        return [['No Students Registered!', 'N/A']]
