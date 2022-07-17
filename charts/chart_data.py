import datetime

from django.db.models import Sum, Count

from charts.chart_tools import unzip, get_colours
from quizzes.models import QuizResults


def chart_topic_points2(student, date_from, date_to):
    # get base queryset
    qs = QuizResults.objects.all()

    # apply requested filters, if any
    if student is not None:
        qs = qs.filter(student=student)
    if date_from is not None:
        qs = qs.filter(date_created__gte=date_from)
    if date_to is not None:
        qs = qs.filter(date_created__lte=date_to)

    points_per_topic = qs.values('topic__name').annotate(Sum('points'))\
        .values_list("topic__name", "points__sum")

    labels_and_data = unzip(points_per_topic)
    if len(labels_and_data) == 0:
        return []
    colours = get_colours(len(labels_and_data[0]))
    label = "Points"

    chart_data = build_chart_data(labels_and_data, colours, label)
    return chart_data


def chart_topic_quizzes2(student, date_from, date_to):
    # get base queryset
    qs = QuizResults.objects.all()

    # apply requested filters, if any
    if student is not None:
        qs = qs.filter(student=student)
    if date_from is not None:
        qs = qs.filter(date_created__gte=date_from)
    if date_to is not None:
        qs = qs.filter(date_created__lte=date_to)

    # quizzes taken per topic
    quizzes_per_topic = qs.values('topic__name').annotate(quizzes_taken=Count('id'))\
        .values_list("topic__name", "quizzes_taken")

    labels_and_data = unzip(quizzes_per_topic)
    if len(labels_and_data) == 0:
        return []
    colours = get_colours(len(labels_and_data[0]))
    label = "Quizzes"

    chart_data = build_chart_data(labels_and_data, colours, label)
    return chart_data


def chart_topic_words2(student):
    student_results = QuizResults.objects.filter(student=student)

    # topics by ratio correct v incorrect answers
    correct_v_incorrect = student_results.values('topic__name').annotate(Sum('correct_answers'),
                                                                         Sum('incorrect_answers'))

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


def chart_points_per_day2(student):
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
    colours = get_colours(len(labels_and_data[0]))

    chart_data = {
        "labels": labels_and_data[0],
        "datasets": [{
            "label": "Points",
            "data": labels_and_data[1],
            "backgroundColor": colours[0],
            "borderColor": ['rgb(75, 192, 192)'],
            "tension": 0.1,
        }]
    }
    return chart_data


def build_chart_data(labels_and_data, colours, label):
    return {
        "labels": labels_and_data[0],
        "datasets": [{
            "label": label,
            "data": labels_and_data[1],
            "backgroundColor": colours[0],
            "borderColor": colours[1],
            "borderWidth": 2,
        }]}
