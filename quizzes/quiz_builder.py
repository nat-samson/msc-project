import random

from quizzes.models import Topic

MAX_QUESTIONS_IN_QUIZ = 12


def get_dummy_data():
    data = [{
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
    ]
    return data


def get_quiz(user, topic_pk):
    # create quiz for given topic
    topic = Topic.objects.get(pk=topic_pk)

    # pool for incorrect multiple-choice options
    options_pool = list(topic.words.values('id', 'origin', 'target'))

    if len(options_pool) < 4:
        return []

    results = []
    words_to_revise = topic.words_due_revision(user).values('id', 'origin', 'target')[:MAX_QUESTIONS_IN_QUIZ]

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

        results.append(question)

    return results
    # return get_dummy_data()


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
