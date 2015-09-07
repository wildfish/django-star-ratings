from random import random, randint
from django.test import TestCase
from model_mommy import mommy
from star_ratings.models import AggregateRating


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
