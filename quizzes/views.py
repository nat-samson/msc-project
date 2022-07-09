import datetime
import json

from django.db.models import FilteredRelation, Q, F
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from quizzes import quiz_builder
from quizzes.models import Topic, Word, WordScore, QuizResults


# temporary basic home view - INACTIVE
def home(request):
    context = {
        'topics': Topic.objects.all()
    }
    return render(request, 'quizzes/home.html', context)


class TopicListView(ListView):
    model = Topic
    template_name = 'quizzes/home.html'
    context_object_name = 'topics'
    ordering = ['date_created']

    #paginate_by = 6  # TODO: Pagination


class TopicDetailView(DetailView):
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


def quiz(request, topic_pk):
    if request.method == 'POST':
        # get the quiz results data out of request.POST
        data = request.POST.get('results')
        results = json.loads(data)

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
                    word_id=word_id, student=request.user,
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

                word_score, is_newly_created = WordScore.objects.get_or_create(word_id=word_id, student=request.user)

                if not is_newly_created:
                    word_score.consecutive_correct = 0
                    word_score.times_seen = F('times_seen') + 1
                    word_score.next_review = datetime.date.today()
                    word_score.save(update_fields=['consecutive_correct', 'times_seen'])

            results_page_data['words'][word_score] = is_correct

        # Log the quiz in the database
        QuizResults.objects.create(student=request.user, topic_id=topic_pk,
                                   correct_answers=correct, incorrect_answers=incorrect)

        # generate and render results page
        results_page_data['correct'] = correct
        results_page_data['total'] = len(results)

        return render(request, 'quizzes/quiz_results.html', results_page_data)

    else:
        # get the quiz and pass it to the template
        questions = quiz_builder.get_quiz(request.user, topic_pk)

        return render(request, 'quizzes/quiz.html', {'questions': questions})
