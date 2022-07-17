import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import render

from charts.chart_data import chart_topic_points2, chart_topic_quizzes2
from charts.chart_tools import unzip, get_colours
from charts.forms import DatePresetFilterForm, DashboardFilterForm
from quizzes.models import Topic, QuizResults, WordScore, MAX_SCORE, Word
from users.models import User


@login_required
def progress(request):
    # obtain non-filterable data
    context = {
        "words_due_revision": Topic.all_topics_words_due_revision(request.user).count(),
        "words_memorised": WordScore.objects.filter(student=request.user,
                                                    word__wordscore__consecutive_correct__gte=MAX_SCORE),
        "current_streak": 0,
        "date_filter": DatePresetFilterForm('filter-date-student'),
    }
    return render(request, 'charts/progress.html', context)


@login_required()
def get_filtered_data_student(request):
    # obtain base queryset
    qs = QuizResults.objects.filter(student=request.user)

    # extract filter settings from request, apply to queryset
    date_range_length = request.GET.get('date_range')
    if date_range_length != "":
        from_date = datetime.date.today() - datetime.timedelta(int(date_range_length))
        qs = qs.filter(date_created__gte=from_date)

    # calculate correct percentage (or N/A if no quizzes completed in timeframe)
    correct_pc = "N/A"
    pc = qs.aggregate(total_correct=Sum('correct_answers'), total_incorrect=Sum('incorrect_answers'))
    total_questions = int(pc['total_correct'] or 0) + int(pc['total_incorrect'] or 0)
    if total_questions > 0:
        correct_pc = f"{(pc['total_correct'] / total_questions):.0%}"

    data = {
        "points_earned": qs.aggregate(total=Sum('points')).get('total') or 0,
        "quizzes_taken": qs.count(),
        "correct_pc": correct_pc,
    }
    return JsonResponse(data)


@login_required()
def get_filtered_data_teacher(request):
    # obtain base queryset
    qs = QuizResults.objects.all()

    # extract filter settings from request, apply to queryset
    date_range_length = request.GET.get('date_range')
    if date_range_length != "":
        from_date = datetime.date.today() - datetime.timedelta(int(date_range_length))
        qs = qs.filter(date_created__gte=from_date)

    data = {
        "active_students": qs.values_list('student', flat=True).distinct().count(),
        "quizzes_taken": qs.count(),
        "points_earned": qs.aggregate(total=Sum('points')).get('total') or 0,
    }
    return JsonResponse(data)


@login_required
def chart_topic_points(request):
    student_results = QuizResults.objects.filter(student=request.user)
    points_per_topic = student_results.values('topic__name').annotate(Sum('points'))\
        .values_list("topic__name", "points__sum")

    labels_and_data = unzip(points_per_topic)
    colours = get_colours(len(labels_and_data[0]))

    chart_data = {
        "labels": labels_and_data[0],
        "datasets": [{
            "label": "Points",
            "data": labels_and_data[1],
            "backgroundColor": colours[0],
            "borderColor": colours[1],
            "borderWidth": 2,
        }]
    }
    return JsonResponse(chart_data)


@login_required
def chart_topic_quizzes(request):
    student_results = QuizResults.objects.filter(student=request.user)

    # quizzes taken per topic
    quizzes_per_topic = student_results.values('topic__name').annotate(quizzes_taken=Count('id'))\
        .values_list("topic__name", "quizzes_taken")

    labels_and_data = unzip(quizzes_per_topic)
    colours = get_colours(len(labels_and_data[0]))

    chart_data = {
        "labels": labels_and_data[0],
        "datasets": [{
            "label": "Quizzes",
            "data": labels_and_data[1],
            "backgroundColor": colours[0],
            "borderColor": colours[1],
            "borderWidth": 2,
        }]
    }
    return JsonResponse(chart_data)


@login_required
def chart_topic_words(request):
    student_results = QuizResults.objects.filter(student=request.user)

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
    colours = get_colours(len(labels_and_data[0]))

    chart_data = {
        "labels": labels_and_data[0],
        "datasets": [{
            "label": "Ratio Correct:Incorrect",
            "data": labels_and_data[1],
            "backgroundColor": colours[0],
            "borderColor": colours[1],
        }]
    }
    return JsonResponse(chart_data)


@login_required
def chart_points_per_day(request):
    today = datetime.date.today()
    date_from = today - datetime.timedelta(28)
    student_results = QuizResults.objects.filter(student=request.user, date_created__gte=date_from)
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
    return JsonResponse(chart_data)


def dashboard(request):
    # obtain non-filterable data
    context = {
        "live_topics": Topic.objects.filter(is_hidden=False).count(),
        "live_words": Word.objects.count(),
        "students_registered": User.objects.filter(is_student=True, is_active=True).count(),
        "date_filter": DatePresetFilterForm('filter-date-teacher'),
        "student_filter": DashboardFilterForm(),
    }
    return render(request, 'charts/dashboard.html', context)


@login_required
def get_student_charts_data(request):
    # check if request has come with a filter request
    if len(request.GET) == 0:
        # if not, request is a student, so capture their ID
        student = request.user.pk
        date_from = None
        date_to = None
    else:
        # request is from teacher, so extract filter settings from request
        filter_settings = {k: v[0] for k, v in dict(request.GET).items() if v[0] != ""}
        student = filter_settings.get('student', None)
        date_from = filter_settings.get('date_from', None)
        date_to = filter_settings.get('date_to', None)

    points_per_topic = chart_topic_points2(student, date_from, date_to)
    quizzes_per_topic = chart_topic_quizzes2(student, date_from, date_to)
    data = {
        "points_per_topic": points_per_topic,
        "quizzes_per_topic": quizzes_per_topic,
    }
    return JsonResponse(data)
