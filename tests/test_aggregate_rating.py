from random import random, randint
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy
from star_ratings.models import AggregateRating
from .models import Foo


class AggregateRatingToDict(TestCase):
    def test_fields_are_present_and_correct(self):
        max_value = randint(0, 10)
        total = random() * max_value
        count = randint(1, 100)
        avg = total / count

        rating = mommy.make(
            AggregateRating,
            max_value=max_value,
            count=count,
            total=total,
            average=avg,
        )

        self.assertEqual(dict(
            max_value=max_value,
            count=count,
            total=total,
            average=avg
        ), rating.to_dict())


class AggregateRatingStr(TestCase):
    def test_result_is_the_same_as_the_context_object(self):
        foo = mommy.make(Foo)

        ratings = AggregateRating.objects.ratings_for_model(foo)

        self.assertEqual(str(foo), str(ratings))


class AggregateRatingOrdering(TestCase):
    def test_order_item_by_average_rating_is_possible(self):
        user_a, user_b = mommy.make(get_user_model(), _quantity=2)
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # Avg. rating: 2.5
        AggregateRating.objects.rate(foo_a, 4, user_a, '127.0.0.1')
        AggregateRating.objects.rate(foo_a, 1, user_b, '127.0.0.1')

        # Avg. rating: 2
        AggregateRating.objects.rate(foo_b, 1, user_b, '127.0.0.1')
        AggregateRating.objects.rate(foo_b, 3, user_a, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__average')
        self.assertEqual(foos[0].pk, foo_b.pk)
        self.assertEqual(foos[1].pk, foo_a.pk)

    def test_order_item_by_count_rating_is_possible(self):
        user_a, user_b = mommy.make(get_user_model(), _quantity=2)
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # 2 ratings
        AggregateRating.objects.rate(foo_a, 4, user_a, '127.0.0.1')
        AggregateRating.objects.rate(foo_a, 1, user_a, '127.0.0.1')

        # 3 ratings
        AggregateRating.objects.rate(foo_b, 2, user_b, '127.0.0.1')
        AggregateRating.objects.rate(foo_b, 3, user_b, '127.0.0.1')
        AggregateRating.objects.rate(foo_b, 2, user_b, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__count')
        self.assertEqual(foos[0].pk, foo_a.pk)
        self.assertEqual(foos[1].pk, foo_b.pk)

    def test_order_item_by_total_rating_is_possible(self):
        user = mommy.make(get_user_model())
        foo_a = self.foo = Foo.objects.create(name='foo a')
        foo_b = self.foo = Foo.objects.create(name='foo b')

        # total rating: 4
        AggregateRating.objects.rate(foo_a, 4, user, '127.0.0.1')

        # total rating: 3
        AggregateRating.objects.rate(foo_b, 3, user, '127.0.0.1')

        foos = Foo.objects.filter(ratings__isnull=False).order_by('ratings__total')
        self.assertEqual(foos[1].pk, foo_a.pk)
        self.assertEqual(foos[0].pk, foo_b.pk)
