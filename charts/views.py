from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render

from charts.chart_data import get_points_per_day_data, get_updatable_charts_data, get_filtered_results, \
    get_points_per_student_data
from charts.forms import DateFilterForm, StudentDateFilterForm, TopicDateFilterForm
from quizzes.models import Topic, WordScore, MAX_SCORE, Word
from users.models import User


@login_required
def progress(request):
    # obtain non-filterable data
    context = {
        "words_due_revision": Topic.all_topics_words_due_revision(request.user).count(),
        "words_memorised": WordScore.objects.filter(student=request.user,
                                                    word__wordscore__consecutive_correct__gte=MAX_SCORE).count(),
        "current_streak": 0,
        "date_filter": DateFilterForm("filter-date-student"),
    }
    return render(request, 'charts/progress.html', context)


@login_required
@user_passes_test(lambda user: user.is_teacher)
def dashboard(request):
    # obtain non-filterable data
    context = {
        "live_topics": Topic.objects.filter(is_hidden=False).count(),
        "live_words": Word.objects.count(),
        "students_registered": User.objects.filter(is_student=True, is_active=True).count(),
        "date_filter": DateFilterForm("filter-date-teacher"),
        "student_filter": StudentDateFilterForm("data-updatable-charts"),
        "topic_filter": TopicDateFilterForm("filter-date-topic"),
    }
    return render(request, 'charts/dashboard.html', context)


@login_required()
def get_filtered_data_student(request):
    # obtain queryset
    qs = get_filtered_results(request)

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


@login_required
@user_passes_test(lambda user: user.is_teacher)
def get_filtered_data_teacher(request):
    # obtain queryset
    qs = get_filtered_results(request)

    data = {
        "active_students": qs.values_list('student', flat=True).distinct().count(),
        "quizzes_taken": qs.count(),
        "points_earned": qs.aggregate(total=Sum('points')).get('total') or 0,
    }
    return JsonResponse(data)


@login_required
@user_passes_test(lambda user: user.is_teacher)
def get_filtered_data_topic(request):
    # obtain queryset
    qs = get_filtered_results(request)

    data = get_points_per_student_data(qs)
    return JsonResponse(data, safe=False)


@login_required
def get_updatable_charts(request):
    # check if request has come with a filter request
    if len(request.GET) == 0:
        # if not, request is from a student, so capture their ID
        student = request.user.pk
        date_from = None
        date_to = None
    else:
        # request is from teacher, so extract filter settings from request
        filter_settings = {k: v[0] for k, v in dict(request.GET).items() if v[0] != ""}
        student = filter_settings.get('student', None)
        date_from = filter_settings.get('date_from', None)
        date_to = filter_settings.get('date_to', None)

    data = get_updatable_charts_data(student, date_from, date_to)
    return JsonResponse(data)


@login_required
def get_points_per_day(request):
    chart_data = get_points_per_day_data(request.user)
    return JsonResponse(chart_data)
