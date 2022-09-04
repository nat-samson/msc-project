# Generated by Django 4.0.5 on 2022-07-28 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0007_alter_word_options_quizresults_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='is_hidden',
            field=models.BooleanField(default=False, help_text='Hide the Topic from view. No quizzes can be taken using this Topic while it is hidden. Topics which contain fewer than four words are hidden regardless.', verbose_name='Hide Topic'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='long_desc',
            field=models.CharField(blank=True, max_length=255, verbose_name='Long Description'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='short_desc',
            field=models.CharField(default='❓🧠❓', help_text='Illustrate the Topic with a few emoji. On Mac? Press CTRL+CMD+Space. On Windows? Press Windows key + fullstop.', max_length=10, verbose_name='Emoji Description'),
        ),
    ]
