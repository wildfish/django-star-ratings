from random import randint
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy
from star_ratings.models import Rating, UserRating
from .models import Foo, Bar


class UserRatingStr(TestCase):
    def test_result_contains_user_id_and_rating_name(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)

        rating = Rating.objects.rate(foo, 1, user, '0.0.0.0')
        user_rating = rating.user_ratings.get(user=user)

        self.assertEqual('{} rating {} for {}'.format(user, user_rating.score, rating.content_object, rating.content_object), str(user_rating))


class UserRatingHasRated(TestCase):
    def setUp(self):
        self.foo = mommy.make(Foo)
        self.bar = mommy.make(Bar)
        self.user_a = mommy.make(get_user_model())
        self.user_b = mommy.make(get_user_model())

    def test_user_has_rated_the_model___results_is_true(self):
        Rating.objects.rate(self.foo, randint(1, 5), self.user_a, '0.0.0.0')

        self.assertTrue(UserRating.objects.has_rated(self.foo, self.user_a))

    def test_different_user_has_rated_the_model___results_is_false(self):
        Rating.objects.rate(self.foo, randint(1, 5), self.user_a, '0.0.0.0')

        self.assertFalse(UserRating.objects.has_rated(self.foo, self.user_b))

    def test_user_has_rated_a_different_model___results_is_false(self):
        Rating.objects.rate(self.foo, randint(1, 5), self.user_a, '0.0.0.0')

        self.assertFalse(UserRating.objects.has_rated(self.bar, self.user_a))

    def test_user_has_rated_a_different_model_instance___results_is_false(self):
        foo2 = mommy.make(Foo)

        Rating.objects.rate(self.foo, randint(1, 5), self.user_a, '0.0.0.0')

        self.assertFalse(UserRating.objects.has_rated(foo2, self.user_a))
