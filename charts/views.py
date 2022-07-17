import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import render

from charts.chart_tools import unzip, get_colours
from charts.forms import DatePresetFilterForm
from quizzes.models import Topic, QuizResults, WordScore, MAX_SCORE


@login_required
def progress(request):
    # provide non-filterable data
    context = {
        "words_due_revision": Topic.all_topics_words_due_revision(request.user).count(),
        "words_memorised": WordScore.objects.filter(student=request.user,
                                                    word__wordscore__consecutive_correct__gte=MAX_SCORE),
        "current_streak": 0,
        "date_filter": DatePresetFilterForm(),
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


@login_required
def chart_topic_points(request):
    student_results = QuizResults.objects.filter(student=request.user)
    points_per_topic = student_results.values('topic__name').annotate(Sum('points')).values_list("topic__name", "points__sum")

    labels_and_data = unzip(points_per_topic)
    colours = get_colours(len(labels_and_data[0]))

    chart_data = {
        "title": "Points Per Topic",
        "backgroundColor": colours[0],
        "borderColor": colours[1],
        "label": "Points",
        "labels": labels_and_data[0],
        "data": labels_and_data[1],
    }
    return JsonResponse(chart_data)


@login_required
def chart_topic_quizzes(request):
    student_results = QuizResults.objects.filter(student=request.user)

    # quizzes taken per topic
    quizzes_per_topic = student_results.values('topic__name').annotate(quizzes_taken=Count('id')).values_list("topic__name", "quizzes_taken")

    labels_and_data = unzip(quizzes_per_topic)
    colours = get_colours(len(labels_and_data[0]))

    chart_data = {
        "title": "Quizzes Taken Per Topic",
        "backgroundColor": colours[0],
        "borderColor": colours[1],
        "label": "Quizzes",
        "labels": labels_and_data[0],
        "data": labels_and_data[1],
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
        "title": "Proportion of Correct to Incorrect Answers",
        "backgroundColor": colours[0],
        "borderColor": colours[1],
        "label": "Ratio Correct:Incorrect",
        "labels": labels_and_data[0],
        "data": labels_and_data[1],
    }
    return JsonResponse(chart_data)
