from __future__ import unicode_literals

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.test import override_settings
from hypothesis import given, Settings
from hypothesis.extra.django import TestCase
from hypothesis.strategies import lists, integers
from model_mommy import mommy
from six import assertRaisesRegex
from tests.strategies import scores
from star_ratings import app_settings
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

        data = res.func()
        self.assertIsInstance(data['rating'], Rating)
        self.assertEqual(item, data['rating'].content_object)

    def test_item_is_rated___rating_object_for_item_is_returned(self):
        item = mommy.make(Foo)

        rating = Rating.objects.for_instance(item)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(rating, data['rating'])

    def test_request_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(request, data['request'])

    def test_request_user_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(request.user, data['user'])

    def test_user_is_authenticated_without_rating_for_object___user_rating_is_none(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')

        request.user = get_user_model().objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertIsNone(data['user_rating'])

    def test_user_is_not_authenticated_with_rating_for_object___user_rating_is_none(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertIsNone(data['user_rating'])

    def test_user_is_authenticated_with_rating_for_object___user_rating_for_user_is_returned(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = get_user_model().objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')

        rating = Rating.objects.rate(item, 3, request.user)
        user_rating = UserRating.objects.get(rating=rating, user=request.user)

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(user_rating, data['user_rating'])

    def test_stars_list_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(list(range(1, app_settings.STAR_RATINGS_RANGE + 1)), data['stars'])

    def test_star_count_is_added_to_the_result(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(app_settings.STAR_RATINGS_RANGE, data['star_count'])

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

        data = res.func()
        expected_avg = 100 * (rating.average / Decimal(app_settings.STAR_RATINGS_RANGE))
        self.assertEqual(expected_avg, data['percentage'])

    def test_icon_height_is_not_set___icon_height_is_32(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(32, data['icon_height'])

    @given(integers())
    def test_icon_height_is_set___icon_height_is_correct(self, height):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item, icon_height=height)

        data = res.func()
        self.assertEqual(height, data['icon_height'])

    def test_icon_width_is_not_set___icon_height_is_32(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertEqual(32, data['icon_width'])

    @given(integers())
    def test_icon_width_is_set___icon_height_is_correct(self, width):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item, icon_width=width)

        data = res.func()
        self.assertEqual(width, data['icon_width'])

    def test_id_is_a_uid_with_dsr_prefix(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item)

        data = res.func()
        self.assertTrue(data['id'].startswith('dsr'))
        self.assertIsNotNone(int(data['id'][3:], 16))

    def test_request_is_not_set_in_context___exception_is_raised(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        with assertRaisesRegex(self, Exception, 'Make sure you have "django.core.context_processors.request" in "TEMPLATE_CONTEXT_PROCESSORS"'):
            ratings({}, item)

    @override_settings(STAR_RATINGS_ANONYMOUS=False)
    def test_read_only_is_false_user_is_not_authenticated_anon_rating_is_false___editable_is_false(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        res = ratings({
            'request': request,
        }, item, read_only=False)

        data = res.func()
        self.assertFalse(data['editable'])
        self.assertFalse(data['read_only'])

    @override_settings(STAR_RATINGS_ANONYMOUS=False)
    def test_read_only_is_false_user_is_authenticated_anon_rating_is_false___editable_is_true(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item, read_only=False)

        data = res.func()
        self.assertTrue(data['editable'])
        self.assertFalse(data['read_only'])

    @override_settings(STAR_RATINGS_ANONYMOUS=True)
    def test_read_only_is_false_user_is_not_authenticated_anon_rating_is_true___editable_is_true(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        res = ratings({
            'request': request,
        }, item, read_only=False)

        data = res.func()
        self.assertTrue(data['editable'])
        self.assertFalse(data['read_only'])

    def test_read_only_is_set_to_true___editable_is_false(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item, read_only=True)

        data = res.func()
        self.assertFalse(data['editable'])
        self.assertTrue(data['read_only'])

    def test_template_name_is_set_in_parameter_and_context___parameter_is_used_as_template_name(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
            'star_ratings_template_name': 'context_template',
        }, item, read_only=True, template_name='parameter_template')

        self.assertEqual(res.filename, 'parameter_template')

    def test_template_name_is_set_in_context___context_is_used_as_template_name(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
            'star_ratings_template_name': 'context_template',
        }, item, read_only=True)

        self.assertEqual(res.filename, 'context_template')

    def test_template_name_is_not_set_in_param_or_context___default_is_used_as_template_name(self):
        item = mommy.make(Foo)

        request = RequestFactory().get('/')
        request.user = mommy.make(get_user_model())

        res = ratings({
            'request': request,
        }, item, read_only=True)

        self.assertEqual(res.filename, 'star_ratings/widget.html')
