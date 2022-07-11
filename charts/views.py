import datetime

from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import render

from charts.chart_tools import unzip, get_colours
from quizzes.models import Topic, QuizResults, Word


def dashboard(request):
    student_results = QuizResults.objects.filter(student=request.user)
    current_week = datetime.datetime.now().isocalendar()[1]

    # calculate weekly correct percentage
    try:
        weekly_pc = student_results.filter(date_created__week=current_week)\
            .aggregate(total_correct=Sum('correct_answers'), total_incorrect=Sum('incorrect_answers'))
        total_questions = weekly_pc['total_correct'] + weekly_pc['total_incorrect']
        pc = "{:.0%}".format(weekly_pc['total_correct'] / total_questions)
    except:
        pc = "0%"

    # initial data for dashboard
    context = {
        "topics_count": Topic.objects.count(),
        "words_due_revision": Topic.all_topics_words_due_revision(request.user).count(),
        "total_words": Word.objects.count(),
        "quizzes_this_week": student_results.filter(date_created__week=current_week).count(),
        "weekly_points": student_results.filter(date_created__week=current_week).aggregate(total=Sum('points')),
        "all_time_points": student_results.aggregate(total=Sum('points')),
        "weekly_correct_pc": pc,
    }

    return render(request, 'charts/dashboard.html', context)


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
