from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from star_ratings.models import AggregateRating


class Foo(models.Model):
    bar = models.CharField(max_length=100)
    ratings = GenericRelation(AggregateRating, related_query_name='foos')

    def __str__(self):
        return self.bar
