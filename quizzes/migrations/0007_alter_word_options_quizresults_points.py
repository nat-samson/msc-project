# Generated by Django 4.0.5 on 2022-07-09 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0006_wordscore_last_updated'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='word',
            options={},
        ),
        migrations.AddField(
            model_name='quizresults',
            name='points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
