import datetime

from django.db.models import Sum, Count

from charts.chart_tools import unzip, get_colours
from quizzes.models import QuizResults, WordScore
from users.models import User


PTS_PER_DAY_DATERANGE = 14  # number of days to display on Progress template linechart
MAX_WEAKEST_WORDS = 10  # maximum number of the weakest words to display


def get_filtered_queryset(request):
    # obtain base queryset
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
    if not qs.exists():
        return {'points_per_topic': [], 'quizzes_per_topic': []}

    points_per_topic_data = get_points_per_topic_data(qs)
    quizzes_per_topic_data = get_quizzes_per_topic_data(qs)

    return {'points_per_topic': points_per_topic_data, 'quizzes_per_topic': quizzes_per_topic_data}


def get_points_per_topic_data(qs):
    points_per_topic = qs.values('topic__name').annotate(Sum('points')).values_list("topic__name", "points__sum")
    label = "Points"

    return prepare_data(points_per_topic, label)


def get_quizzes_per_topic_data(qs):
    quizzes_per_topic = qs.values('topic__name').annotate(quizzes_taken=Count('id'))\
        .values_list("topic__name", "quizzes_taken")
    label = "Quizzes"

    return prepare_data(quizzes_per_topic, label)


def get_weakest_words_data(student=False):
    # rank words by % incorrect answers
    scores = WordScore.objects.all()
    if student:
        scores = WordScore.objects.filter(student=student)

    weakest_words = list(scores.values('word').annotate(incorrect_pc=Sum('times_correct')*100/Sum('times_seen'))
                         .order_by('incorrect_pc')
                         .values_list('word__origin', 'word__target', 'incorrect_pc')[:MAX_WEAKEST_WORDS])

    while len(weakest_words) < MAX_WEAKEST_WORDS:
        weakest_words.append(("N/A", "N/A", "N/A"))

    return weakest_words


def get_points_per_day_data(student):
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
    # only includes students who have completed a quiz within date range
    pts_per_student = list(qs.values('student').annotate(Sum('points'))
                           .values_list('student__first_name', 'student__last_name', "points__sum")
                           .order_by('-points__sum', 'student__last_name'))

    # add in students who have no quiz data
    missing_students = User.objects.filter(is_teacher=False).exclude(quizresults__in=qs).order_by('last_name')

    present_student_data = [(f"{student[0]} {student[1]}", student[2]) for student in pts_per_student]
    missing_student_data = [(student.get_full_name(), 0) for student in missing_students]
    final_data = present_student_data + missing_student_data

    if final_data:
        return final_data
    else:
        return [["No Students Registered!", "N/A"]]


def prepare_data(data, label, override_colours=False):
    labels_and_data = unzip(data)

    if override_colours:
        colours = override_colours
    else:
        colours = get_colours(len(labels_and_data[0]))

    return format_for_chart_js(labels_and_data, colours, label)


def format_for_chart_js(labels_and_data, colours, label):
    # set up some common chart data and insert specific chart data
    return {
        "labels": labels_and_data[0],
        "datasets": [{
            "label": label,
            "data": labels_and_data[1],
            "backgroundColor": colours[0],
            "borderColor": colours[1],
            "borderWidth": 2,
            "tension": 0.2,
        }]
    }
