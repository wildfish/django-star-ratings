from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy
from star_ratings.models import AggregateRating, Rating
from .models import Foo


class RatingManagerHasRated(TestCase):
    def test_has_rate_is_passed_a_aggregate_rating_instance___type_error_is_raised(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_model(foo)

        with self.assertRaisesRegex(TypeError, "Rating manager 'has_rated' expects model to be rated, not AggregateRating model."):
            Rating.objects.has_rated(ratings, user)
