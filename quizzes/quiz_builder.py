from django.http import JsonResponse

from quizzes.models import Word, WordScore


def get_dummy_data():

    data = [{
                'word_id': 3,
                'target_to_origin': True,
                'word': 'Mouse',
                'correct_answer': 0,
                'options': ['Die Maus', 'Der Bär', 'Der Hund', 'Die Katze']
            },
            {
                'word_id': 2,
                'target_to_origin': True,
                'word': 'Dog',
                'correct_answer': 1,
                'options': ['Die Maus', 'Der Hund', 'Die Katze', 'Der Bär']
            },
            {
                'word_id': 1,
                'target_to_origin': False,
                'word': 'Die Katze',
                'correct_answer': 1,
                'options': ['Dog', 'Cat', 'Bear', 'Mouse']
            }]

    return data


def get_quiz(user, topic_pk):
    # create quiz for given topic

    # TODO: check user is actually registered for the course containing the topic

    #words_in_topic = Word.objects.filter(topics=topic_pk)
    #user_word_scores = WordScore.objects.filter(student=user, word__topics=topic_pk)

    return get_dummy_data()
