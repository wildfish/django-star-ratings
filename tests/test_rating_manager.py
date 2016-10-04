from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from hypothesis import given, Settings
from hypothesis.strategies import lists, tuples
from hypothesis.extra.django import TestCase
from mock import patch
from model_mommy import mommy
from star_ratings.models import Rating
from .models import Foo
from tests.strategies import scores
from six import assertRaisesRegex


def mean(nums):
    """
    Our own mean function, as Python 2 doesn't include the statistics module.
    """
    return float(sum(nums)) / len(nums)


class RatingManagerForInstance(TestCase):
    def test_rating_object_exists_for_model___that_object_is_returned(self):
        item = mommy.make(Foo)
        rating = mommy.make(Rating, content_object=item)

        res = Rating.objects.for_instance(item)

        self.assertEqual(rating, res)

    def test_rating_object_does_not_exist_for_model___object_is_created_and_returned(self):
        item = mommy.make(Foo)

        res = Rating.objects.for_instance(item)

        self.assertIsInstance(res, Rating)
        self.assertEqual(item, res.content_object)
        self.assertEqual(0, res.count)
        self.assertEqual(0, res.total)
        self.assertEqual(0, res.average)

    def test_passed_a_rating_instance___type_error_is_raised(self):
        item = mommy.make(Foo)
        ratings = Rating.objects.for_instance(item)

        with assertRaisesRegex(self, TypeError, "Rating manager 'for_instance' expects model to be rated, not Rating model."):
            Rating.objects.for_instance(ratings)


class RatingManagerRate(TestCase):
    def setUp(self):
        self.user_a = mommy.make(get_user_model())
        self.user_b = mommy.make(get_user_model())
        self.foo = Foo.objects.create()

    @given(scores())
    def test_user_rates_object___rating_object_is_create(self, score):
        ratings = Rating.objects.rate(self.foo, score, self.user_a, '127.0.0.1')
        rating = ratings.user_ratings.get(user=self.user_a)

        self.assertEqual(score, rating.score)

    @given(lists(scores(), min_size=2), settings=Settings(max_examples=5))
    def test_multiple_users_rating_the_object___aggregates_are_updated(self, scores):
        ratings = None
        for score in scores:
            ratings = Rating.objects.rate(self.foo, score, mommy.make(get_user_model()), '127.0.0.1')

        self.assertEqual(ratings.count, len(scores))
        self.assertAlmostEqual(ratings.total, sum(scores))
        self.assertAlmostEqual(ratings.average, mean(scores))

    @given(lists(scores(), min_size=2), settings=Settings(max_examples=5))
    def test_deleting_the_rating___aggregates_are_updated(self, scores):
        ratings = None
        for score in scores:
            ratings = Rating.objects.rate(self.foo, score, mommy.make(get_user_model()), '127.0.0.1')

        removed_score = scores.pop()
        ratings.user_ratings.filter(score=removed_score).first().delete()

        self.assertEqual(ratings.count, len(scores))
        self.assertAlmostEqual(ratings.total, sum(scores))
        self.assertAlmostEqual(ratings.average, mean(scores))

    @override_settings(STAR_RATINGS_RERATE=True)
    @given(tuples(scores(), scores()).filter(lambda x: x[0] != x[1]))
    def test_same_user_rate_twice_rerate_is_true___rating_is_changed(self, scores):
        first, second = scores

        ratings = Rating.objects.rate(self.foo, first, self.user_a, '127.0.0.1')
        self.assertTrue(ratings.user_ratings.filter(user=self.user_a, score=first))
        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, first)
        self.assertEqual(ratings.average, first)

        ratings = Rating.objects.rate(self.foo, second, self.user_a, '127.0.0.1')
        self.assertTrue(ratings.user_ratings.filter(user=self.user_a, score=second))
        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, second)
        self.assertEqual(ratings.average, second)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_same_user_rate_twice_rerate_is_false___validation_error_is_raised(self):
        """
        If re-rating is disabled the rating should not count
        """
        ratings = Rating.objects.rate(self.foo, 4, self.user_a, '127.0.0.1')
        with self.assertRaises(ValidationError):
            ratings = Rating.objects.rate(self.foo, 2, self.user_a, '127.0.0.1')

        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, 4)
        self.assertEqual(ratings.average, 4)

    def test_rate_is_passed_a_rating_instance___value_error_is_raised(self):
        ratings = Rating.objects.for_instance(self.foo)

        with assertRaisesRegex(self, TypeError, "Rating manager 'rate' expects model to be rated, not Rating model."):
            Rating.objects.rate(ratings, 2, self.user_a, '127.0.0.1')


class RatingsForInstanceDeprication(TestCase):
    def test_ratings_for_instance_is_called___deprication_warning_is_given(self):
        foo = Foo.objects.create()

        with patch('star_ratings.models.warn') as warn_mock:
            Rating.objects.ratings_for_instance(foo)

            warn_mock.assert_called_once_with("RatingManager method 'ratings_for_instance' has been renamed to 'for_instance'. Please change uses of 'Rating.objects.ratings_for_instance' to 'Rating.objects.for_instance' in your code.", DeprecationWarning)

    def test_ratings_for_instance_is_called___for_instance_is_called_with_the_correct_instance(self):
        foo = Foo.objects.create()

        with patch('star_ratings.models.RatingManager.for_instance') as for_instance_mock:
            Rating.objects.ratings_for_instance(foo)

            for_instance_mock.assert_called_once_with(foo)
