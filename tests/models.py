from __future__ import unicode_literals

import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from star_ratings import get_star_ratings_rating_model_name
from star_ratings.models import AbstractBaseRating


class Foo(models.Model):
    name = models.CharField(max_length=100)
    ratings = GenericRelation(get_star_ratings_rating_model_name(), related_query_name='foos')

    def __str__(self):
        return self.name


class Bar(models.Model):
    name = models.CharField(max_length=100)
    ratings = GenericRelation(get_star_ratings_rating_model_name(), related_query_name='bars')

    def __str__(self):
        return self.name


class FooWithUUID(Foo):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)


class MyRating(AbstractBaseRating):
    object_id = models.UUIDField(null=True, blank=True)
    foo = models.TextField()
