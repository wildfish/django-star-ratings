from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from model_mommy import mommy
from star_ratings.models import AggregateRating
from .models import Foo


class RatingsTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='user_a', password='pwd')
        self.user_b = User.objects.create_user(username='user_b', password='pwd')
        self.foo = Foo.objects.create()

    def test_auto_create_ratings(self):
        """
        Auto generate an aggregate model for an object
        """
        ratings = AggregateRating.objects.ratings_for_model(self.foo)
        self.assertEqual(ratings.count, 0)
        self.assertEqual(ratings.total, 0)
        self.assertEqual(ratings.average, 0)

    def test_rate_model(self):
        """
        Two different users rating the same model
        """
        ratings = AggregateRating.objects.ratings_for_model(self.foo)

        ratings = AggregateRating.objects.rate(ratings, 4, self.user_a, '127.0.0.1')
        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, 4)
        self.assertEqual(ratings.average, 4)

        ratings = AggregateRating.objects.rate(ratings, 3, self.user_b, '127.0.0.2')
        self.assertEqual(ratings.count, 2)
        self.assertEqual(ratings.total, 7)
        self.assertEqual(ratings.average, 3.5)

    def test_same_user_rate_twice(self):
        """
        Same user rating a model twice
        """
        ratings = AggregateRating.objects.ratings_for_model(self.foo)
        ratings = AggregateRating.objects.rate(ratings, 4, self.user_a, '127.0.0.1')
        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, 4)
        self.assertEqual(ratings.average, 4)

        ratings = AggregateRating.objects.rate(ratings, 2, self.user_a, '127.0.0.1')
        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, 2)
        self.assertEqual(ratings.average, 2)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_rerating_disabled(self):
        """
        If re-rating is disabled the rating should not count
        """
        ratings = AggregateRating.objects.ratings_for_model(self.foo)
        ratings = AggregateRating.objects.rate(ratings, 4, self.user_a, '127.0.0.1')
        with self.assertRaises(ValidationError):
            ratings = AggregateRating.objects.rate(ratings, 2, self.user_a, '127.0.0.1')

        self.assertEqual(ratings.count, 1)
        self.assertEqual(ratings.total, 4)
        self.assertEqual(ratings.average, 4)

    def test_order_by_average_rating(self):
        foo_a = self.foo = Foo.objects.create(bar='foo a')
        foo_b = self.foo = Foo.objects.create(bar='foo b')
        rating_a = AggregateRating.objects.ratings_for_model(foo_a)
        rating_b = AggregateRating.objects.ratings_for_model(foo_b)

        # Avg. rating: 3.5
        AggregateRating.objects.rate(rating_a, 4, self.user_a, '127.0.0.1')
        AggregateRating.objects.rate(rating_b, 3, self.user_b, '127.0.0.1')

        # Avg. rating: 1.5
        AggregateRating.objects.rate(rating_a, 1, self.user_a, '127.0.0.1')
        AggregateRating.objects.rate(rating_b, 2, self.user_b, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__average')
        self.assertEqual(foos[0].pk, foo_a.pk)
        self.assertEqual(foos[1].pk, foo_b.pk)


class AggregateRatingStr(TestCase):
    def test_result_is_the_same_as_the_context_object(self):
        foo = mommy.make(Foo)

        ratings = AggregateRating.objects.ratings_for_model(foo)

        self.assertEqual(str(foo), str(ratings))


class RatingStr(TestCase):
    def test_result_contains_user_id_and_aggregate_rating_name(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)

        ratings = AggregateRating.objects.ratings_for_model(foo)
        AggregateRating.objects.rate(ratings, 1, user, '0.0.0.0')
        rating = ratings.ratings.get(user=user)

        self.assertEqual('User {} rating for {}'.format(user.pk, ratings), str(rating))
