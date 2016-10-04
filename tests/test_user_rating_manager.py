from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from model_mommy import mommy
from star_ratings.models import Rating, UserRating
from .models import Foo
from six import assertRaisesRegex


class RatingManagerHasRated(TestCase):
    def test_has_rate_is_passed_a_rating_instance___type_error_is_raised(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        with assertRaisesRegex(self, TypeError, "UserRating manager 'has_rated' expects model to be rated, not UserRating model."):
            UserRating.objects.has_rated(ratings, user)


class ForInstanceByUser(TestCase):
    @override_settings(STAR_RATINGS_ANONYMOUS=False)
    def test_anon_ratings_is_false_user_not_set___value_error_is_raised(self):
        foo = mommy.make(Foo)

        with assertRaisesRegex(self, ValueError, "User is mandatory. Enable 'STAR_RATINGS_ANONYMOUS' for anonymous ratings."):
            UserRating.objects.for_instance_by_user(foo)

    @override_settings(STAR_RATINGS_ANONYMOUS=True)
    def test_anon_ratings_is_true___none_is_returned(self):
        foo = mommy.make(Foo)

        Rating.objects.rate(foo, 1, ip='127.0.0.1')
        Rating.objects.rate(foo, 1, ip='127.0.0.1')

        self.assertIsNone(
            UserRating.objects.for_instance_by_user(foo),
        )

    def test_user_is_set___rating_object_for_is_returned(self):
        foo = mommy.make(Foo)
        user = mommy.make(get_user_model())

        Rating.objects.rate(foo, 1, user=mommy.make(get_user_model()))
        expected = Rating.objects.rate(foo, 1, user=user).user_ratings.get(user=user)

        self.assertEqual(
            expected,
            UserRating.objects.for_instance_by_user(foo, user=user),
        )
