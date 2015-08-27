from django.test import TestCase
from model_mommy import mommy
from wildfish_ratings.models import RateableModel
from .models import Foo


class RateableModelManagerRatingsForItem(TestCase):
    def test_ratable_model_object_exists_for_item___that_object_is_returned(self):
        item = mommy.make(Foo)
        ratable_object = mommy.make(RateableModel, content_object=item)

        res = RateableModel.objects.ratings_for_item(item)

        self.assertEqual(ratable_object, res)

    def test_ratable_model_object_does_not_exist_for_item___object_is_created_and_returned(self):
        item = mommy.make(Foo)

        res = RateableModel.objects.ratings_for_item(item)

        self.assertIsInstance(res, RateableModel)
        self.assertEqual(item, res.content_object)
