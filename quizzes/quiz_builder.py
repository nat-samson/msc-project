import copy
import random
import datetime

from django.shortcuts import get_object_or_404

from quizzes.models import Topic

MAX_QUIZ_LENGTH = 12
CORRECT_ANSWER_PTS = 10
ORIGIN_ICON = "🇬🇧"
TARGET_ICON = "🇩🇪"


def get_dummy_data():
    data = {
        'correct_pts': CORRECT_ANSWER_PTS,
        'origin_icon': ORIGIN_ICON,
        'target_icon': TARGET_ICON,
        'is_due_revision': True,
        'questions': [
            {
                'word_id': 3,
                'origin_to_target': True,
                'word': 'Mouse',
                'correct_answer': 0,
                'options': ['Die Maus', 'Der Bär', 'Der Hund', 'Die Katze']
            },
            {
                'word_id': 2,
                'origin_to_target': True,
                'word': 'Dog',
                'correct_answer': 1,
                'options': ['Die Maus', 'Der Hund', 'Die Katze', 'Der Bär']
            },
            {
                'word_id': 1,
                'origin_to_target': False,
                'word': 'Die Katze',
                'correct_answer': 1,
                'options': ['Dog', 'Cat', 'Bear', 'Mouse']
            },
            {
                'word_id': 7,
                'origin_to_target': False,
                'word': 'Der Fisch',
                'correct_answer': 3,
                'options': ['Cat', 'Mouse', 'Bear', 'Fish']
            }
        ],
    }
    return data


def get_quiz_template():
    return {
        'correct_pts': CORRECT_ANSWER_PTS,
        'origin_icon': ORIGIN_ICON,
        'target_icon': TARGET_ICON,
        'is_due_revision': True,
    }


def get_quiz(user, topic_id):
    """ create quiz for given topic """

    # teachers can still do quizzes if topic is hidden, or not yet launched
    if user.is_teacher:
        topic = get_object_or_404(Topic, pk=topic_id)
    else:
        topic = get_object_or_404(Topic, pk=topic_id, is_hidden=False, available_from__lte=datetime.date.today())

    quiz = get_quiz_template()
    questions = []

    # gather data needed for the quiz: the words due to be revised, and a pool of possible incorrect options
    words_to_revise = topic.words_due_revision(user).values('id', 'origin', 'target')[:MAX_QUIZ_LENGTH]
    options_pool = list(topic.words.values('id', 'origin', 'target')[:MAX_QUIZ_LENGTH * 4])

    # ensure both word lists have enough content with which to form a quiz
    if len(words_to_revise) == 0:
        quiz['is_due_revision'] = False
        try:
            words_to_revise = random.sample(copy.deepcopy(options_pool), MAX_QUIZ_LENGTH)
        except ValueError:
            pass

    if len(options_pool) >= 4:
        for question in words_to_revise:
            direction = choose_direction()
            question['origin_to_target'] = direction

            options = get_options(options_pool, question['id'], direction)

            correct_answer = random.randrange(4)
            question['correct_answer'] = correct_answer

            if direction:
                options.insert(correct_answer, question.pop('target'))
                question['word'] = question.pop('origin')
            else:
                options.insert(correct_answer, question.pop('origin'))
                question['word'] = question.pop('target')

            question['options'] = options
            question['word_id'] = question.pop('id')

            questions.append(question)

    quiz['questions'] = questions

    return quiz


def get_options(options_pool, word_id, direction):
    if not direction:
        option_text = 'origin'
    else:
        option_text = 'target'

    raw_options = random.sample(options_pool, 4)  # pick 4 in case one of those is the correct answer

    # remove the correct answer if selected
    options = (opt[option_text] for opt in raw_options if opt['id'] != word_id)
    return [next(options) for _ in range(3)]


def choose_direction():
    return bool(random.randrange(2))
