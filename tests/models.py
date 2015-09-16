from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from star_ratings.models import Rating


class Foo(models.Model):
    name = models.CharField(max_length=100)
    ratings = GenericRelation(Rating, related_query_name='foos')

    def __str__(self):
        return self.name


class Bar(models.Model):
    name = models.CharField(max_length=100)
    ratings = GenericRelation(Rating, related_query_name='bars')

    def __str__(self):
        return self.name
