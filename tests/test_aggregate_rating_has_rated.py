import random
from model_mommy import mommy
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Foo
from star_ratings.models import AggregateRating


class RatableModelHasRated(TestCase):
    def test_user_has_not_rated_the_model___results_is_false(self):
        foo = mommy.make(Foo)
        user = mommy.make(get_user_model())

        self.assertFalse(AggregateRating.objects.has_rated(foo, user))

    def test_user_has_rated_the_model___results_is_false(self):
        foo = mommy.make(Foo)
        user = mommy.make(get_user_model())

        AggregateRating.objects.rate(foo, random.randint(1, 5), user, '0.0.0.0')

        self.assertTrue(AggregateRating.objects.has_rated(foo, user))
