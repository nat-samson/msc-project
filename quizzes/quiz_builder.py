from django.http import JsonResponse

from quizzes.models import Word, WordScore


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

    #words_in_topic = Word.objects.filter(topics=topic_pk)
    #user_word_scores = WordScore.objects.filter(student=user, word__topics=topic_pk)

    return get_dummy_data()
