# Generated by Django 4.0.5 on 2022-06-30 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0004_alter_wordscore_times_seen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wordscore',
            name='score',
        ),
    ]
