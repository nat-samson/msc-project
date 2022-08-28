import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import FilteredRelation, Q, F, Count, ExpressionWrapper, BooleanField
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView

from quizzes import quiz_builder
from quizzes.models import Topic, Word, WordScore, QuizResults
from quizzes.quiz_builder import CORRECT_ANSWER_PTS


class HomeView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'quizzes/home.html'
    context_object_name = 'topics'
    ordering = ['date_created']

    def get_queryset(self):
        # topics that are hidden, future-scheduled, or have fewer than 4 words, are only visible to teachers
        today = datetime.date.today()
        topics = Topic.objects.annotate(
            word_count=Count('words'),
            future_avail_from=ExpressionWrapper(Q(available_from__gt=today), output_field=BooleanField()),
            is_visible=ExpressionWrapper(Q(is_hidden=False) & Q(future_avail_from=False), output_field=BooleanField()))

        if not self.request.user.is_teacher:
            # exclude such non-visible topics from students
            topics = topics.filter(is_visible=True, word_count__gte=4)
        return topics


class TopicDetailView(LoginRequiredMixin, DetailView):
    # model tells the view which model to use to create the detail view
    model = Topic
    fields = ['name', 'long_desc', 'short_desc']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the queryset for all words in Topic and their scores, even if no WordScore exists yet
        qs = Word.objects.filter(topics=context['topic'])\
            .annotate(joinscore=FilteredRelation('wordscore', condition=Q(wordscore__student=self.request.user)),)\
            .order_by('origin')\
            .values_list('origin', 'target', 'joinscore__consecutive_correct', 'joinscore__next_review')

        # adjust words with no WordScores to sensible default values, or when date is in past
        words_with_scores = []
        today = datetime.date.today()

        for word in qs:
            if word[2] is None:
                words_with_scores.append((word[0], word[1], 0, today))
            elif word[3] < today:
                words_with_scores.append((word[0], word[1], word[2], today))
            else:
                words_with_scores.append(word)

        context['words_with_scores'] = words_with_scores
        return context


class QuizView(LoginRequiredMixin, View):
    def post(self, *args, topic_id, **kwargs):
        # get the quiz results data out of request.POST
        data = self.request.POST.get('results')
        results = json.loads(data)
        student = self.request.user

        results_page_data = process_results(results, student, topic_id)
        self.request.session['results'] = results_page_data
        return redirect(self.request.path)

    def get(self, *args, topic_id, **kwargs):
        # get the quiz and pass it to the template
        results = self.request.session.get('results', False)
        if results:
            del self.request.session['results']
            return render(self.request, 'quizzes/quiz_results.html', results)
        else:
            quiz_data = quiz_builder.get_quiz(self.request.user, topic_id=topic_id)

            if quiz_data['questions']:
                return render(self.request, 'quizzes/quiz.html', {'quiz': quiz_data})

            # handle the race condition if a topic doesn't have enough words after the quiz is requested
            else:
                return redirect(reverse('home'))


def process_results(results, student, topic_id, today=datetime.date.today()):
    results_page_data = {'words': {}}
    correct = 0
    incorrect = 0

    # process the results
    for word_id, is_correct in results.items():

        # answer is correct
        if is_correct:
            correct += 1

            word_score, is_newly_created = WordScore.objects.get_or_create(
                word_id=word_id, student=student,
                defaults={'consecutive_correct': 1, 'times_correct': 1,
                          'next_review': today + datetime.timedelta(days=1)})

            # only update score if it was due for review
            if not is_newly_created:
                if word_score.next_review <= today:
                    word_score.set_next_review(today=today)
                    word_score.consecutive_correct = F('consecutive_correct') + 1
                    word_score.times_seen = F('times_seen') + 1
                    word_score.times_correct = F('times_correct') + 1
                    word_score.save(update_fields=['consecutive_correct', 'times_seen',
                                                   'times_correct', 'next_review'])

        # answer is incorrect
        else:
            incorrect += 1

            word_score, is_newly_created = WordScore.objects.get_or_create(word_id=word_id, student=student)

            if not is_newly_created:
                word_score.consecutive_correct = 0
                word_score.times_seen = F('times_seen') + 1
                word_score.next_review = today
                word_score.save(update_fields=['consecutive_correct', 'times_seen'])

        # prepare data for display on the results page
        results_page_data['words'][word_score.pk] = {
            'origin': word_score.word.origin,
            'target': word_score.word.target,
            'is_correct': is_correct,
        }
    # Update user's streak if this is their first quiz taken today
    QuizResults.update_user_streak(student, today=today)
    # log quiz results in the database
    quiz_score = correct * CORRECT_ANSWER_PTS
    QuizResults.objects.create(student=student, topic_id=topic_id,
                               correct_answers=correct, incorrect_answers=incorrect,
                               points=quiz_score, date_created=today)
    # record quiz score and pass it to results page
    results_page_data['correct'] = correct
    results_page_data['total'] = len(results)
    return results_page_data
