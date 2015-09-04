import random
from model_mommy import mommy
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Foo
from wildfish_ratings.models import RateableModel


class RatableModelHasRated(TestCase):
    def test_user_has_not_rated_the_model___results_is_false(self):
        foo = mommy.make(Foo)
        user = mommy.make(get_user_model())

        ratings = RateableModel.objects.ratings_for_item(foo)
        self.assertFalse(RateableModel.objects.has_rated(ratings, user))

    def test_user_has_rated_the_model___results_is_false(self):
        foo = mommy.make(Foo)
        user = mommy.make(get_user_model())

        ratings = RateableModel.objects.ratings_for_item(foo)
        RateableModel.objects.rate(ratings, random.randint(1, 5), user, '0.0.0.0')

        self.assertTrue(RateableModel.objects.has_rated(foo, user))
