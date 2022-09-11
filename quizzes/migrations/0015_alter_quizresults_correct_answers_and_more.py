# Generated by Django 4.0.5 on 2022-09-11 11:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0014_alter_topic_available_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizresults',
            name='correct_answers',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='quizresults',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='quizresults',
            name='incorrect_answers',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='word',
            name='topics',
            field=models.ManyToManyField(blank=True, related_name='words', to='quizzes.topic'),
        ),
        migrations.AlterField(
            model_name='wordscore',
            name='consecutive_correct',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='wordscore',
            name='times_correct',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='wordscore',
            name='times_seen',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
