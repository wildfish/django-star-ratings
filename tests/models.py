from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from star_ratings.models import Rating


@python_2_unicode_compatible
class Foo(models.Model):
    name = models.CharField(max_length=100)
    ratings = GenericRelation(Rating, related_query_name='foos')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Bar(models.Model):
    name = models.CharField(max_length=100)
    ratings = GenericRelation(Rating, related_query_name='bars')

    def __str__(self):
        return self.name
