from django.db import models


# most essential model fields to get started
class Topic(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=100, blank=True)
    is_hidden = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)


class Word(models.Model):
    origin = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='words')
    date_created = models.DateTimeField(auto_now_add=True)
