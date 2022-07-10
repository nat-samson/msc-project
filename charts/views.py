import datetime

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render

from quizzes.models import Topic, QuizResults, Word


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
    data = {
        "sales": 50,
        "customers": 5,
    }
    return JsonResponse(data)
