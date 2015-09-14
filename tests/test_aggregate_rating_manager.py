from statistics import mean
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from hypothesis import given, Settings
from hypothesis.strategies import lists, tuples
from hypothesis.extra.django import TestCase
from model_mommy import mommy
from star_ratings.models import AggregateRating
from .models import Foo
from tests.strategies import scores


class AggregateRatingManagerRatingsForItem(TestCase):
    def test_aggregate_object_exists_for_model___that_object_is_returned(self):
        item = mommy.make(Foo)
        aggregate = mommy.make(AggregateRating, content_object=item)

        res = AggregateRating.objects.ratings_for_model(item)

        self.assertEqual(aggregate, res)

    def test_aggregate_object_does_not_exist_for_model___object_is_created_and_returned(self):
        item = mommy.make(Foo)

        res = AggregateRating.objects.ratings_for_model(item)

        self.assertIsInstance(res, AggregateRating)
        self.assertEqual(item, res.content_object)
        self.assertEqual(0, res.count)
        self.assertEqual(0, res.total)
        self.assertEqual(0, res.average)


class AggregateRatingManagerRate(TestCase):
    def setUp(self):
        self.user_a = mommy.make(get_user_model())
        self.user_b = mommy.make(get_user_model())
        self.foo = Foo.objects.create()

    @given(scores())
    def test_user_rates_object___rating_object_is_create(self, score):
        ratings = AggregateRating.objects.rate(self.foo, score, self.user_a, '127.0.0.1')
        rating = ratings.ratings.get(user=self.user_a)

        self.assertEqual(score, rating.score)

    @given(lists(scores(), min_size=2), settings=Settings(max_examples=5))
    def test_multiple_users_rating_the_object___aggregates_are_updated(self, scores):
        ratings = None
        for score in scores:
            ratings = AggregateRating.objects.rate(self.foo, score, mommy.make(get_user_model()), '127.0.0.1')

        self.assertEqual(ratings.count, len(scores))
        self.assertAlmostEqual(ratings.total, sum(scores))
        self.assertAlmostEqual(ratings.average, mean(scores))

    @given(lists(scores(), min_size=2), settings=Settings(max_examples=5))
    def test_deleting_the_rating___aggregates_are_updated(self, scores):
        ratings = None
        for score in scores:
            ratings = AggregateRating.objects.rate(self.foo, score, mommy.make(get_user_model()), '127.0.0.1')

        removed_score = scores.pop()
        ratings.ratings.filter(score=removed_score).first().delete()

        self.assertEqual(ratings.count, len(scores))
        self.assertAlmostEqual(ratings.total, sum(scores))
        self.assertAlmostEqual(ratings.average, mean(scores))

    @override_settings(STAR_RATINGS_RERATE=True)
    @given(tuples(scores(), scores()).filter(lambda x: x[0] != x[1]))
    def test_same_user_rate_twice_rerate_is_true___rating_is_changed(self, scores):
        first, second = scores

        ratings = AggregateRating.objects.rate(self.foo, first, self.user_a, '127.0.0.1')
        self.assertTrue(ratings.ratings.filter(user=self.user_a, score=first))
        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, first)
        self.assertEqual(ratings.average, first)

        ratings = AggregateRating.objects.rate(self.foo, second, self.user_a, '127.0.0.1')
        self.assertTrue(ratings.ratings.filter(user=self.user_a, score=second))
        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, second)
        self.assertEqual(ratings.average, second)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_same_user_rate_twice_rerate_is_false___validation_error_is_raised(self):
        """
        If re-rating is disabled the rating should not count
        """
        ratings = AggregateRating.objects.rate(self.foo, 4, self.user_a, '127.0.0.1')
        with self.assertRaises(ValidationError):
            ratings = AggregateRating.objects.rate(self.foo, 2, self.user_a, '127.0.0.1')

        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, 4)
        self.assertEqual(ratings.average, 4)
