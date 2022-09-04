import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import FilteredRelation, Q, F, Count, ExpressionWrapper, BooleanField
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView

from quizzes.utils import quiz_builder
from quizzes.models import Topic, Word
from quizzes.utils.quiz_logger import process_results


class HomeView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'quizzes/home.html'
    context_object_name = 'topics'
    ordering = ['date_created']

    def get_queryset(self):
        # topics that are hidden, future-scheduled, or have fewer than 4 words, are only visible to teachers
        today = datetime.date.today()
        topics = Topic.objects.annotate(
            word_count=Count('words', distinct=True),
            future_avail_from=ExpressionWrapper(Q(available_from__gt=today), output_field=BooleanField()),
            is_visible=ExpressionWrapper(Q(is_hidden=False) & Q(future_avail_from=False), output_field=BooleanField()))

        if not self.request.user.is_teacher:
            # exclude non-visible topics from students' homepage, add details of words due revision
            student = self.request.user
            topics = topics.filter(is_visible=True, word_count__gte=4)\
                .annotate(words_due=F('word_count') - Count('id', filter=Q(words__wordscore__next_review__gt=today) &
                                                            Q(words__wordscore__student=student)))

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
