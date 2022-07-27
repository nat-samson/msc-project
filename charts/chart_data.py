import datetime

from django.db.models import Sum, Count

from charts.chart_tools import unzip, get_colours
from quizzes.models import QuizResults
from users.models import User


def get_updatable_charts_data(student, date_from, date_to):
    # get base queryset
    qs = QuizResults.objects.all()

    # apply requested filters, if any
    if student is not None:
        qs = qs.filter(student=student)
    if date_from is not None:
        qs = qs.filter(date_created__gte=date_from)
    if date_to is not None:
        qs = qs.filter(date_created__lte=date_to)

    points_per_topic_data = get_points_per_topic_data(qs)
    quizzes_per_topic_data = get_quizzes_per_topic_data(qs)

    return {'points_per_topic': points_per_topic_data, 'quizzes_per_topic': quizzes_per_topic_data}


def get_points_per_topic_data(qs):
    points_per_topic = qs.values('topic__name').annotate(Sum('points')).values_list("topic__name", "points__sum")

    labels_and_data = unzip(points_per_topic)
    if len(labels_and_data) == 0:
        return []
    colours = get_colours(len(labels_and_data[0]))
    label = "Points"

    chart_data = build_chart_data(labels_and_data, colours, label)
    return chart_data


def get_quizzes_per_topic_data(qs):
    quizzes_per_topic = qs.values('topic__name').annotate(quizzes_taken=Count('id'))\
        .values_list("topic__name", "quizzes_taken")

    labels_and_data = unzip(quizzes_per_topic)
    if len(labels_and_data) == 0:
        return []
    colours = get_colours(len(labels_and_data[0]))
    label = "Quizzes"

    chart_data = build_chart_data(labels_and_data, colours, label)
    return chart_data


def get_topic_correctness_data(qs):
    # topics by ratio correct v incorrect answers
    correct_v_incorrect = qs.values('topic__name').annotate(Sum('correct_answers'), Sum('incorrect_answers'))

    # calculate ratio correct:incorrect by topic and rank by highest to lowest
    correct_v_incorrect_list = []
    for topic in correct_v_incorrect:
        topic_name = topic['topic__name']
        value = topic['correct_answers__sum'] / (topic['correct_answers__sum'] + topic['incorrect_answers__sum'])
        correct_v_incorrect_list.append((topic_name, value))
    correct_v_incorrect_list.sort(reverse=True, key=lambda x: x[1])

    labels_and_data = unzip(correct_v_incorrect_list)
    if len(labels_and_data) == 0:
        return []
    colours = get_colours(len(labels_and_data[0]))
    label = "Ratio Correct:Incorrect"

    chart_data = build_chart_data(labels_and_data, colours, label)
    return chart_data


def get_points_per_day_data(student):
    today = datetime.date.today()
    date_from = today - datetime.timedelta(28)
    student_results = QuizResults.objects.filter(student=student, date_created__gte=date_from)
    points_per_day = list(student_results.values('date_created').annotate(total_points=Sum('points'))
                          .order_by('date_created').values_list('date_created', 'total_points'))

    # fill in missing days
    if len(points_per_day) < 28:
        dates_present = [data_point[0] for data_point in points_per_day]
        for day in range(28):
            date = date_from + datetime.timedelta(day)
            if date not in dates_present:
                points_per_day.insert(day, (date, 0))

    labels_and_data = unzip(points_per_day)
    if len(labels_and_data) == 0:
        return []
    colours = ['rgba(75, 192, 192, 1)', 'rgba(75, 192, 192, 1)']  # line charts look better with same colour nodes
    label = "Points"

    chart_data = build_chart_data(labels_and_data, colours, label)
    return chart_data


def get_points_per_student_data(qs):
    # only includes students who have completed a quiz within date range
    pts_per_student = list(qs.values('student').annotate(Sum('points'))
                           .values_list('student__first_name', 'student__last_name', "points__sum")
                           .order_by('-points__sum', 'student__last_name'))

    # add in students who have no quiz data
    missing_students = User.objects.filter(is_student=True).exclude(quizresults__in=qs).order_by('last_name')

    present_student_data = [(f"{student[0]} {student[1]}", student[2]) for student in pts_per_student]
    missing_student_data = [(student.get_full_name(), 0) for student in missing_students]
    final_data = present_student_data + missing_student_data

    if final_data:
        return final_data
    else:
        return [["No Students Registered!", "N/A"]]


def build_chart_data(labels_and_data, colours, label):
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
        }]}


def get_filtered_results(request):
    # obtain base queryset
    qs = QuizResults.objects.filter(student__is_student=True)

    # extract filter settings from GET request, apply to queryset
    date_range_length = request.GET.get('date_range', "")
    if date_range_length != "":
        from_date = datetime.date.today() - datetime.timedelta(int(date_range_length))
        qs = qs.filter(date_created__gte=from_date)

    topic = request.GET.get('topic', "")
    if topic != "":
        qs = qs.filter(topic_id=topic)

    print(request.GET)

    return qs
