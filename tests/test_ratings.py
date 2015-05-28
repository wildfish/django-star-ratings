from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from .models import Foo
from wildfish_ratings.models import RateableModel


class RatingsTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='user_a', password='pwd')
        self.user_b = User.objects.create_user(username='user_b', password='pwd')
        self.inactive_user = User.objects.create_user(username='user_c', password='pwd')
        self.inactive_user.is_active = False
        self.inactive_user.save()
        self.foo = Foo.objects.create()

    def test_auto_create_ratings(self):
        """
        Auto generate a ratable model for an object
        """
        ratings = RateableModel.objects.ratings_for_item(self.foo)
        self.assertEqual(ratings.rating_count, 0)
        self.assertEqual(ratings.rating_total, 0)
        self.assertEqual(ratings.rating_average, 0)

    def test_rate_model(self):
        """
        Two different users rating the same model
        """
        ratings = RateableModel.objects.ratings_for_item(self.foo)

        ratings = RateableModel.objects.rate(ratings, 4, self.user_a, '127.0.0.1')
        self.assertEqual(ratings.rating_count, 1)
        self.assertEqual(ratings.rating_total, 4)
        self.assertEqual(ratings.rating_average, 4)

        ratings = RateableModel.objects.rate(ratings, 3, self.user_b, '127.0.0.2')
        self.assertEqual(ratings.rating_count, 2)
        self.assertEqual(ratings.rating_total, 7)
        self.assertEqual(ratings.rating_average, 3.5)

    def test_same_user_rate_twice(self):
        """
        Same user rating a model twice
        """
        ratings = RateableModel.objects.ratings_for_item(self.foo)
        ratings = RateableModel.objects.rate(ratings, 4, self.user_a, '127.0.0.1')
        self.assertEqual(ratings.rating_count, 1)
        self.assertEqual(ratings.rating_total, 4)
        self.assertEqual(ratings.rating_average, 4)

        ratings = RateableModel.objects.rate(ratings, 2, self.user_a, '127.0.0.1')
        self.assertEqual(ratings.rating_count, 1)
        self.assertEqual(ratings.rating_total, 2)
        self.assertEqual(ratings.rating_average, 2)

    def test_unverified_cant_rate(self):
        """
        Ensure that a user that is not verified can't rate
        """
        ratings = RateableModel.objects.ratings_for_item(self.foo)
        with self.assertRaises(ValidationError):
            RateableModel.objects.rate(ratings, 2, self.inactive_user, '127.0.0.1')

    @override_settings(WILDFISH_RATINGS_RERATE=False)
    def test_rerating_disabled(self):
        """
        If re-rating is disabled the rating should not count
        """
        ratings = RateableModel.objects.ratings_for_item(self.foo)
        ratings = RateableModel.objects.rate(ratings, 4, self.user_a, '127.0.0.1')
        with self.assertRaises(ValidationError):
            ratings = RateableModel.objects.rate(ratings, 2, self.user_a, '127.0.0.1')

        self.assertEqual(ratings.rating_count, 1)
        self.assertEqual(ratings.rating_total, 4)
        self.assertEqual(ratings.rating_average, 4)

    def test_order_by_average_rating(self):
        foo_a = self.foo = Foo.objects.create(bar='foo a')
        foo_b = self.foo = Foo.objects.create(bar='foo b')
        rating_a = RateableModel.objects.ratings_for_item(foo_a)
        rating_b = RateableModel.objects.ratings_for_item(foo_b)

        # Avg. rating: 3.5
        RateableModel.objects.rate(rating_a, 4, self.user_a, '127.0.0.1')
        RateableModel.objects.rate(rating_b, 3, self.user_b, '127.0.0.1')

        # Avg. rating: 1.5
        RateableModel.objects.rate(rating_a, 1, self.user_a, '127.0.0.1')
        RateableModel.objects.rate(rating_b, 2, self.user_b, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__rating_average')
        self.assertEqual(foos[0].pk, foo_a.pk)
        self.assertEqual(foos[1].pk, foo_b.pk)
