from random import random, randint
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
