import random
from model_mommy import mommy
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Foo, Bar
from star_ratings.models import AggregateRating, Rating


class RatingHasRated(TestCase):
    def setUp(self):
        self.foo = mommy.make(Foo)
        self.bar = mommy.make(Bar)
        self.user_a = mommy.make(get_user_model())
        self.user_b = mommy.make(get_user_model())

    def test_user_has_not_rated_the_model___results_is_false(self):
        self.assertFalse(Rating.objects.has_rated(self.foo, self.user_a))
        self.assertFalse(Rating.objects.has_rated(self.foo, self.user_b))
        self.assertFalse(Rating.objects.has_rated(self.bar, self.user_a))
        self.assertFalse(Rating.objects.has_rated(self.bar, self.user_b))

    def test_user_has_rated_the_model___results_is_false(self):
        AggregateRating.objects.rate(self.bar, random.randint(1, 5), self.user_a, '0.0.0.0')
        AggregateRating.objects.rate(self.foo, random.randint(1, 5), self.user_b, '0.0.0.0')

        self.assertFalse(Rating.objects.has_rated(self.foo, self.user_a))
        self.assertTrue(Rating.objects.has_rated(self.foo, self.user_b))
        self.assertTrue(Rating.objects.has_rated(self.bar, self.user_a))
        self.assertFalse(Rating.objects.has_rated(self.bar, self.user_b))
