import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import FilteredRelation, Q, F
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
        # hidden or future-scheduled topics are only visible to teachers
        topics = Topic.objects.all()
        if not self.request.user.is_teacher:
            topics = topics.filter(is_hidden=False, available_from__lte=datetime.date.today())
        return topics


class TopicDetailView(LoginRequiredMixin, DetailView):
    # model tells the view which model to use to create the detail view
    model = Topic
    fields = ['name', 'long_desc', 'short_desc']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get the current user's word scores for the given topic (using an outer join with WordScore)
        context['words_with_scores'] = Word.objects.filter(topics=context['topic']).annotate(
            joinscore=FilteredRelation('wordscore', condition=Q(wordscore__student=self.request.user)),
        ).values_list('origin', 'target', 'joinscore__consecutive_correct', 'joinscore__next_review')

        return context


class QuizView(LoginRequiredMixin, View):
    def post(self, *args, topic_id, **kwargs):
        # get the quiz results data out of request.POST
        data = self.request.POST.get('results')
        results = json.loads(data)
        student = self.request.user

        results_page_data = {'words': {}}
        today = datetime.date.today()
        correct = 0
        incorrect = 0

        # process the results
        # likely more efficient to cache all the WordScores of the relevant topic here, use that going forward
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
                        word_score.set_next_review()
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
                    word_score.next_review = datetime.date.today()
                    word_score.save(update_fields=['consecutive_correct', 'times_seen'])

            # prepare data for display on the results page
            results_page_data['words'][word_score.pk] = {
                'origin': word_score.word.origin,
                'target': word_score.word.target,
                'is_correct': is_correct,
            }

        # Update user's streak if this is their first quiz taken today
        QuizResults.update_user_streak(student)

        # log quiz results in the database
        quiz_score = correct * CORRECT_ANSWER_PTS
        QuizResults.objects.create(student=student, topic_id=topic_id,
                                   correct_answers=correct, incorrect_answers=incorrect,
                                   points=quiz_score)

        # record quiz score and pass it to results page
        results_page_data['correct'] = correct
        results_page_data['total'] = len(results)
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
