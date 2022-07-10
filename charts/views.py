import datetime
from collections import Counter


from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import render

from charts.chart_tools import unzip, get_colours
from quizzes.models import Topic, QuizResults, Word
from users.models import User


def dashboard(request):
    student_results = QuizResults.objects.filter(student=request.user)
    current_week = datetime.datetime.now().isocalendar()[1]

    # calculate weekly correct percentage
    weekly_pc = student_results.filter(date_created__week=current_week)\
        .aggregate(total_correct=Sum('correct_answers'), total_incorrect=Sum('incorrect_answers'))
    total_questions = weekly_pc['total_correct'] + weekly_pc['total_incorrect']
    if total_questions == 0:
        pc = "0%"
    else:
        pc = "{:.0%}".format(weekly_pc['total_correct'] / total_questions)

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


def get_data(request):
    student_results = QuizResults.objects.filter(student=request.user)

    #points per topic
    points_per_topic = student_results.values('topic__name').annotate(Sum('points')).values_list("topic__name", "points__sum")
    #thing = Counter([topic[0] for topic in points_per_topic])

    # quizzes taken per topic
    quizzes_per_topic = student_results.values('topic__name').annotate(quizzes_taken=Count('id'))

    # topics ranked by correct v incorrect answers
    correct_v_incorrect = student_results.values('topic__name').annotate(mistakes=Sum('correct_answers')-Sum('incorrect_answers')).order_by('-mistakes')

    labels_and_data = unzip(points_per_topic)
    colours = unzip(get_colours(len(labels_and_data)))

    chart_data = {
        "type": "bar",
        "backgroundColor": colours[0],
        "borderColor": colours[1],
        "label": "All-time Points Per Topic",
        "labels": labels_and_data[0],
        "data": labels_and_data[1],
    }
    return JsonResponse(chart_data)
