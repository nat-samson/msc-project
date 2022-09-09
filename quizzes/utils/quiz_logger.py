import datetime

from django.db import transaction
from django.db.models import F

from myproject.settings import CORRECT_ANSWER_PTS
from quizzes.models import WordScore, QuizResults, Word


@transaction.atomic
def process_results(results, student, topic_id, today=datetime.date.today()):
    """Update the spaced repetition schedule for the User with the latest Quiz data."""
    results_page_data = {'words': []}
    total_questions = 0
    total_correct = 0

    # obtain all the database entries required for maintaining the spaced-repetition schedule
    words_in_quiz = Word.objects.in_bulk(results, field_name='pk')
    word_scores = {str(ws.word_id): ws for ws in
                   WordScore.objects.select_related('word').filter(student=student, word__in=words_in_quiz)}
    word_scores_to_create = []
    word_scores_to_update = []

    # process the results
    for word_id, is_correct in results.items():
        total_questions += 1

        # if WordScore exists for this word/student pair, update it...
        word_score = word_scores.get(word_id, None)

        if word_score:
            if word_score.next_review <= today or not is_correct:
                word_score.times_seen = F('times_seen') + 1

                if is_correct:
                    word_score.set_next_review(today=today)
                    word_score.consecutive_correct = F('consecutive_correct') + 1
                    word_score.times_correct = F('times_correct') + 1
                else:
                    word_score.next_review = today
                    word_score.consecutive_correct = 0
                word_scores_to_update.append(word_score)

        # ...otherwise, create the WordScore
        else:
            if is_correct:
                word_score = WordScore(word=words_in_quiz.get(int(word_id)), student=student, consecutive_correct=1,
                                       times_correct=1, next_review=today + datetime.timedelta(1))
            else:
                word_score = WordScore(word=words_in_quiz.get(int(word_id)), student=student)
            word_scores_to_create.append(word_score)

        # prepare data for display on the results page
        total_correct += is_correct
        result = (word_score.word.origin, word_score.word.target, is_correct)
        results_page_data['words'].append(result)

    # bulk create/update the WordScores
    WordScore.objects.bulk_create(word_scores_to_create)
    WordScore.objects.bulk_update(word_scores_to_update,
                                  fields=['consecutive_correct', 'times_seen', 'times_correct', 'next_review'])

    _log_results(student, today, topic_id, total_correct, total_questions)

    # record quiz score and pass it to results page
    results_page_data['correct'] = total_correct
    results_page_data['total'] = total_questions
    return results_page_data


def _log_results(student, today, topic_id, total_correct, total_questions):
    """Log quiz results in the database."""
    quiz_score = total_correct * CORRECT_ANSWER_PTS
    QuizResults.objects.create(student=student, topic_id=topic_id,
                               correct_answers=total_correct, incorrect_answers=total_questions - total_correct,
                               points=quiz_score, date_created=today)

    # update user's streak if this is their first quiz taken today
    QuizResults.update_user_streak(student, today=today)
