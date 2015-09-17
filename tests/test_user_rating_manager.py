from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy
from star_ratings.models import Rating, UserRating
from .models import Foo
from six import assertRaisesRegex


class RatingManagerHasRated(TestCase):
    def test_has_rate_is_passed_a_rating_instance___type_error_is_raised(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        with assertRaisesRegex(self, TypeError, "UserRating manager 'has_rated' expects model to be rated, not UserRating model."):
            UserRating.objects.has_rated(ratings, user)
