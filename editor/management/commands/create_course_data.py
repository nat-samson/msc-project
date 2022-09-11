import csv

from django.core.management import BaseCommand

from quizzes.models import Topic, Word


class Command(BaseCommand):
    """Terminal command for creating new Topics and Words from CSV files."""

    help = 'Create Topics and Words from topics.csv, words.csv'

    def handle(self, *args, **kwargs):
        # Create TOPICS
        with open('editor/management/commands/topics.csv', 'r', encoding='utf-8') as topics_file:
            reader = csv.DictReader(topics_file)
            topics_to_create = []

            for row in reader:
                [row.pop(key) for key in row.keys() if row[key] == ""]
                topics_to_create.append(Topic(**row))

            topics = Topic.objects.bulk_create(topics_to_create, ignore_conflicts=True)
            topic_words = {topic.name: [] for topic in topics}

            print("Topics done!")

        # Create WORDS
        with open('editor/management/commands/words.csv', 'r') as words_file:
            reader = csv.DictReader(words_file)
            words_to_create = []

            for row in reader:
                [row.pop(key) for key in row.keys() if row[key] == ""]
                topic_names = row.pop('topics').split(';')
                word = Word(**row)
                words_to_create.append(word)

                # extract topic data
                for topic in topic_names:
                    if topic in topic_words:
                        topic_words[topic].append(word.origin)

            Word.objects.bulk_create(words_to_create, ignore_conflicts=True)

            # add each Word to its associated Topics
            for topic, words in topic_words.items():
                words_to_add = Word.objects.in_bulk(words, field_name='origin').values()
                Topic.objects.get(name=topic).words.add(*words_to_add)

            print("Words done!")
