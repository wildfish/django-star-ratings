from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from wildfish_ratings.models import RateableModel


class Foo(models.Model):
    bar = models.CharField(max_length=100)
    ratings = GenericRelation(RateableModel, related_query_name='foos')

    def __str__(self):
        return self.bar
