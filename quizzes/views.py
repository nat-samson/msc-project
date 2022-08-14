import datetime
import json

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import FilteredRelation, Q, F, Count
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, FormView

from quizzes import quiz_builder
from quizzes.forms import TopicForm, WordForm
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
            topics = topics.annotate(word_count=Count('words')).filter(
                is_hidden=False, available_from__lte=datetime.date.today(), word_count__gte=4)
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


class TopicCreateView(UserPassesTestMixin, FormView):
    template_name = 'quizzes/topic_form.html'
    form_class = TopicForm
    created_topic = None

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_teacher

    def get_success_url(self):
        # redirect teacher to the add words page if new topic created successfully
        return reverse('topic_words', kwargs={'topic_id': self.created_topic.id})

    def form_valid(self, form):
        self.created_topic = form.save()
        return super().form_valid(form)


class TopicWordsView(UserPassesTestMixin, ListView):
    model = Word
    template_name = 'quizzes/topic_words.html'
    context_object_name = 'words'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_teacher

    def get_queryset(self):
        topic = get_object_or_404(Topic, pk=self.kwargs.get('topic_id'))
        return Word.objects.filter(topics=topic).order_by(Lower('origin'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic_id'] = self.kwargs.get('topic_id')
        return context


@user_passes_test(lambda user: user.is_authenticated and user.is_teacher)
def add_word(request, topic_id=None):
    """ Obtain (and validate) the HTML form to add a new word """
    data = dict()

    # Process a completed new Word form
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            new_word = form.save()
            if topic_id is not None:
                new_word.topics.add(Topic.objects.get(id=topic_id))
            data['is_valid'] = True

            topic = get_object_or_404(Topic, pk=topic_id)
            words = Word.objects.filter(topics=topic).order_by(Lower('origin'))
            data['html_word_rows'] = render_to_string('quizzes/word_list.html', {'words': words})

        else:
            data['is_valid'] = False

    # Otherwise, create a new blank Word form
    else:
        form = WordForm()

    context = {'form': form}
    data['html_form'] = render_to_string('quizzes/word_form.html', context, request=request)
    return JsonResponse(data)
