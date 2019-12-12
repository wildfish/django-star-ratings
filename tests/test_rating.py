from __future__ import unicode_literals

from hypothesis import given
from hypothesis.strategies import text
from hypothesis.extra.django import TestCase
from random import random, randint
from model_mommy import mommy
from star_ratings import app_settings, get_star_ratings_rating_model
from .fakes import fake_user, fake_rating
from .models import Foo


class RatingToDict(TestCase):
    def test_fields_are_present_and_correct(self):
        total = random() * app_settings.STAR_RATINGS_RANGE
        count = randint(1, 100)
        average = total / count

        rating = fake_rating(
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

        ratings = get_star_ratings_rating_model().objects.for_instance(foo)

        self.assertEqual(str(foo), str(ratings))

    @given(text(min_size=1))
    def test_object_name_contains_any_unicode___str_does_not_error(self, name):
        foo = mommy.make(Foo, name=name)

        ratings = get_star_ratings_rating_model().objects.for_instance(foo)

        self.assertEqual(str(foo), str(ratings))


class RatingOrdering(TestCase):
    def test_order_item_by_average_rating_is_possible(self):
        user_a, user_b = fake_user(_quantity=2)
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # Avg. rating: 2.5
        get_star_ratings_rating_model().objects.rate(foo_a, 4, user_a, '127.0.0.1')
        get_star_ratings_rating_model().objects.rate(foo_a, 1, user_b, '127.0.0.1')

        # Avg. rating: 2
        get_star_ratings_rating_model().objects.rate(foo_b, 1, user_b, '127.0.0.1')
        get_star_ratings_rating_model().objects.rate(foo_b, 3, user_a, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__average')
        self.assertEqual(foos[0].pk, foo_b.pk)
        self.assertEqual(foos[1].pk, foo_a.pk)

    def test_order_item_by_count_rating_is_possible(self):
        user_a, user_b = fake_user(_quantity=2)
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # 2 ratings
        get_star_ratings_rating_model().objects.rate(foo_a, 4, user_a, '127.0.0.1')
        get_star_ratings_rating_model().objects.rate(foo_a, 1, user_a, '127.0.0.1')

        # 3 ratings
        get_star_ratings_rating_model().objects.rate(foo_b, 2, user_b, '127.0.0.1')
        get_star_ratings_rating_model().objects.rate(foo_b, 3, user_b, '127.0.0.1')
        get_star_ratings_rating_model().objects.rate(foo_b, 2, user_b, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__count')
        self.assertEqual(foos[0].pk, foo_a.pk)
        self.assertEqual(foos[1].pk, foo_b.pk)

    def test_order_item_by_total_rating_is_possible(self):
        user = fake_user()
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # total rating: 4
        get_star_ratings_rating_model().objects.rate(foo_a, 4, user, '127.0.0.1')

        # total rating: 3
        get_star_ratings_rating_model().objects.rate(foo_b, 3, user, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__total')
        self.assertEqual(foos[1].pk, foo_a.pk)
        self.assertEqual(foos[0].pk, foo_b.pk)
