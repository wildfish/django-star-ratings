from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from hypothesis import given, Settings
from hypothesis.extra.django import TestCase
from hypothesis.strategies import lists, integers
from model_mommy import mommy
from six import assertRaisesRegex
from tests.strategies import scores
from star_ratings.app_settings import STAR_RATINGS_RANGE
from star_ratings.models import Rating, UserRating
from star_ratings.templatetags.ratings import ratings
from tests.models import Foo


class TemplateTagdRatings(TestCase):
    def test_item_is_not_yet_rated___rating_object_for_item_is_returned(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertIsInstance(res['rating'], Rating)
        self.assertEqual(item, res['rating'].content_object)

    def test_item_is_rated___rating_object_for_item_is_returned(self):
        item = mommy.make(Foo)

        rating = Rating.objects.for_instance(item)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(rating, res['rating'])

    def test_request_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(request, res['request'])

    def test_request_user_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(request.user, res['user'])

    def test_user_is_authenticated_without_rating_for_object___user_rating_is_none(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())
        request.user.is_authenticated = lambda: True

        res = ratings({
            'request': request,
        }, item)

        self.assertIsNone(res['user_rating'])

    def test_user_is_not_authenticated_with_rating_for_object___user_rating_is_none(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())
        request.user.is_authenticated = lambda: False

        Rating.objects.rate(item, 3, request.user)

        res = ratings({
            'request': request,
        }, item)

        self.assertIsNone(res['user_rating'])

    def test_user_is_authenticated_with_rating_for_object___user_rating_for_user_is_returned(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())
        request.user.is_authenticated = lambda: True

        rating = Rating.objects.rate(item, 3, request.user)
        user_rating = UserRating.objects.get(rating=rating, user=request.user)

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(user_rating, res['user_rating'])

    def test_stars_list_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(list(range(1, STAR_RATINGS_RANGE + 1)), res['stars'])

    def test_star_count_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(STAR_RATINGS_RANGE, res['star_count'])

    @given(scores=lists(scores()), settings=Settings(max_examples=5))
    def test_several_ratings_are_made___percentage_is_correct_in_result(self, scores):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        for score in scores:
            Rating.objects.rate(item, score, mommy.make(get_user_model()))

        rating = Rating.objects.for_instance(item)

        res = ratings({
            'request': request,
        }, item)

        expected_avg = 100 * (rating.average / Decimal(STAR_RATINGS_RANGE))
        self.assertEqual(expected_avg, res['percentage'])

    def test_icon_height_is_not_set___icon_height_is_32(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(32, res['icon_height'])

    @given(integers())
    def test_icon_height_is_set___icon_height_is_correct(self, height):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item, icon_height=height)

        self.assertEqual(height, res['icon_height'])

    def test_icon_width_is_not_set___icon_height_is_32(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertEqual(32, res['icon_width'])

    @given(integers())
    def test_icon_width_is_set___icon_height_is_correct(self, width):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item, icon_width=width)

        self.assertEqual(width, res['icon_width'])

    def test_id_is_a_uid_with_dsr_prefix(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        self.assertTrue(res['id'].startswith('dsr'))
        self.assertIsNotNone(int(res['id'][3:], 16))

    def test_request_is_not_set_in_context___exception_is_raised(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        with assertRaisesRegex(self, Exception, 'Make sure you have "django.core.context_processors.request" in "TEMPLATE_CONTEXT_PROCESSORS"'):
            ratings({}, item)
