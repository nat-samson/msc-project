from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render

from charts.forms import DateFilterForm, StudentDateFilterForm, TopicDateFilterForm
from charts.utils.chart_data import get_points_per_day_data, get_updatable_charts_data, get_filtered_queryset, \
    get_points_per_student_data, get_weakest_words_data, get_student_streaks_data
from quizzes.models import Topic, WordScore, MAX_SCORE, Word, QuizResults
from users.models import User

"""
TEMPLATE VIEWS
"""


@login_required
def progress(request):
    """View function responsible for passing all the initial data required by the Progress page."""
    context = {
        "words_due_revision": Topic.all_topics_words_due_revision(request.user).count(),
        "words_memorised": WordScore.objects.filter(student=request.user,
                                                    word__wordscore__consecutive_correct__gte=MAX_SCORE).count(),
        "current_streak": QuizResults.get_user_streak(request.user),
        "date_filter": DateFilterForm("filter-date-student"),
        "weakest_words": get_weakest_words_data(request.user),
    }
    return render(request, 'charts/progress.html', context)


@login_required
@user_passes_test(lambda user: user.is_teacher)
def dashboard(request):
    """View function responsible for passing all the initial data required by the Dashboard page."""
    context = {
        "live_topics": Topic.live_topics().count(),
        "live_words": Word.objects.filter(topics__in=Topic.live_topics().values_list('id')).distinct().count(),
        "students_registered": User.objects.filter(is_teacher=False, is_active=True).count(),
        "date_filter": DateFilterForm("filter-date-teacher"),
        "student_filter": StudentDateFilterForm("data-updatable-charts"),
        "topic_filter": TopicDateFilterForm("filter-date-topic"),
        "weakest_words": get_weakest_words_data(),
        "student_streaks": get_student_streaks_data(),
    }
    return render(request, 'charts/dashboard.html', context)


"""
API VIEWS
"""


@login_required()
def get_filtered_data_student(request):
    """Get the student's filtered data required for the 'databoxes' on the Progress page in JSON format."""
    qs = get_filtered_queryset(request)

    # calculate percentage of correct answers (or "N/A" if no quizzes completed in timeframe)
    pc = qs.aggregate(total_correct=Sum('correct_answers'), total_incorrect=Sum('incorrect_answers'))
    total_questions = int(pc['total_correct'] or 0) + int(pc['total_incorrect'] or 0)
    if total_questions > 0:
        correct_pc = f"{(pc['total_correct'] / total_questions):.0%}"
    else:
        correct_pc = "N/A"

    data = {
        "points_earned": qs.aggregate(total=Sum('points')).get('total') or 0,
        "quizzes_taken": qs.count(),
        "correct_pc": correct_pc,
    }
    return JsonResponse(data)


@login_required
@user_passes_test(lambda user: user.is_teacher)
def get_filtered_data_teacher(request):
    """Get the filtered data required for the 'databoxes' on the Dashboard page in JSON format."""
    qs = get_filtered_queryset(request)
    data = qs.aggregate(active_students=Count('student', distinct=True),
                        quizzes_taken=Count('id'),
                        points_earned=Coalesce(Sum('points'), 0))

    return JsonResponse(data)


@login_required
@user_passes_test(lambda user: user.is_teacher)
def get_filtered_data_topic(request):
    """Get the filtered data required for the Points Per Student table on the Dashboard page in JSON format."""
    qs = get_filtered_queryset(request)

    data = get_points_per_student_data(qs)
    return JsonResponse(data, safe=False)


@login_required
def get_updatable_charts(request):
    """Get the filtered data required for the updatable charts on the Dashboard and Progress pages in JSON format."""
    qs = get_filtered_queryset(request)

    data = get_updatable_charts_data(qs)
    return JsonResponse(data)


@login_required
def get_points_per_day(request):
    """Get the student points per day data required for the Progress page's line chart in JSON format."""
    chart_data = get_points_per_day_data(request.user)
    return JsonResponse(chart_data)
