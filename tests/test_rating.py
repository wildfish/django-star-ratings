from __future__ import unicode_literals

from hypothesis import given
from hypothesis.strategies import text
from random import random, randint
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy
from star_ratings import app_settings
from star_ratings.models import Rating
from .models import Foo


class RatingToDict(TestCase):
    def test_fields_are_present_and_correct(self):
        total = random() * app_settings.STAR_RATINGS_RANGE
        count = randint(1, 100)
        average = total / count

        rating = mommy.make(
            Rating,
            count=count,
            total=total,
            average=average,
        )

        self.assertEqual(dict(
            count=count,
            total=total,
            average=average,
            percentage=rating.percentage,
        ), rating.to_dict())


class RatingStr(TestCase):
    def test_result_is_the_same_as_the_context_object(self):
        foo = mommy.make(Foo)

        ratings = Rating.objects.for_instance(foo)

        self.assertEqual(str(foo), str(ratings))

    @given(text(min_size=1))
    def test_object_name_contains_any_unicode___str_does_not_error(self, name):
        foo = mommy.make(Foo, name=name)

        ratings = Rating.objects.for_instance(foo)

        self.assertEqual(str(foo), str(ratings))


class RatingOrdering(TestCase):
    def test_order_item_by_average_rating_is_possible(self):
        user_a, user_b = mommy.make(get_user_model(), _quantity=2)
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # Avg. rating: 2.5
        Rating.objects.rate(foo_a, 4, user_a, '127.0.0.1')
        Rating.objects.rate(foo_a, 1, user_b, '127.0.0.1')

        # Avg. rating: 2
        Rating.objects.rate(foo_b, 1, user_b, '127.0.0.1')
        Rating.objects.rate(foo_b, 3, user_a, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__average')
        self.assertEqual(foos[0].pk, foo_b.pk)
        self.assertEqual(foos[1].pk, foo_a.pk)

    def test_order_item_by_count_rating_is_possible(self):
        user_a, user_b = mommy.make(get_user_model(), _quantity=2)
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # 2 ratings
        Rating.objects.rate(foo_a, 4, user_a, '127.0.0.1')
        Rating.objects.rate(foo_a, 1, user_a, '127.0.0.1')

        # 3 ratings
        Rating.objects.rate(foo_b, 2, user_b, '127.0.0.1')
        Rating.objects.rate(foo_b, 3, user_b, '127.0.0.1')
        Rating.objects.rate(foo_b, 2, user_b, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__count')
        self.assertEqual(foos[0].pk, foo_a.pk)
        self.assertEqual(foos[1].pk, foo_b.pk)

    def test_order_item_by_total_rating_is_possible(self):
        user = mommy.make(get_user_model())
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # total rating: 4
        Rating.objects.rate(foo_a, 4, user, '127.0.0.1')

        # total rating: 3
        Rating.objects.rate(foo_b, 3, user, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__total')
        self.assertEqual(foos[1].pk, foo_a.pk)
        self.assertEqual(foos[0].pk, foo_b.pk)
