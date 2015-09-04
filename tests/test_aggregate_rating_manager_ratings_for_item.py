from django.test import TestCase
from model_mommy import mommy
from wildfish_ratings.models import AggregateRating
from .models import Foo


class AggregateRatingManagerRatingsForItem(TestCase):
    def test_aggregate_object_exists_for_item___that_object_is_returned(self):
        item = mommy.make(Foo)
        aggregate = mommy.make(AggregateRating, content_object=item)

        res = AggregateRating.objects.ratings_for_item(item)

        self.assertEqual(aggregate, res)

    def test_aggregate_object_does_not_exist_for_item___object_is_created_and_returned(self):
        item = mommy.make(Foo)

        res = AggregateRating.objects.ratings_for_item(item)

        self.assertIsInstance(res, AggregateRating)
        self.assertEqual(item, res.content_object)
