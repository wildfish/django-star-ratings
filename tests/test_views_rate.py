from __future__ import unicode_literals

import json
import pytest
from random import randint
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import override_settings, Client, TestCase
from model_mommy import mommy
from star_ratings.models import Rating, UserRating
from .models import Foo


@pytest.mark.django_db
class TestViewRate(TestCase):
    csrf_checks = False
    client = Client(REMOTE_ADDR='127.0.0.1')

    def post_json(self, url, data, **kwargs):
        if 'user' in kwargs:
            self.client.login(username=kwargs['user'].username, password='password')
        if 'xhr' in kwargs:
            return self.client.post(url, json.dumps(data), content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return self.client.post(url, json.dumps(data), content_type='application/json')

    def get_user(self):
        return get_user_model().objects.create_user(
            username='username',
            first_name='first',
            last_name='last',
            email='example@example.com',
            password='password'
        )

    @override_settings(STAR_RATINGS_ANONYMOUS=False)
    def test_view_is_called_when_nobody_is_logged_in_and_anon_ratings_is_false___user_is_forwarded_to_login(self):
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.post_json(url, {'score': 1})

        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url, fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_ANONYMOUS=True)
    def test_view_is_called_when_nobody_is_logged_in_and_anon_ratings_is_true___rating_is_created(self):
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        self.post_json(url, {'score': score})

        ct = ContentType.objects.get_for_model(foo)

        self.assertTrue(UserRating.objects.filter(rating__object_id=foo.pk, rating__content_type=ct, score=score, ip='127.0.0.1').exists())

    def test_user_is_logged_in_and_doesnt_already_have_a_rating___rating_is_created(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        self.post_json(url, {'score': score}, user=user)

        ct = ContentType.objects.get_for_model(foo)

        self.assertTrue(UserRating.objects.filter(user=user, rating__object_id=foo.pk, rating__content_type=ct, score=score).exists())

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_no_next_url_is_given___redirected_to_root(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_next_url_is_given___redirected_to_next(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_request_is_ajax___rating_is_created(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))

        self.post_json(url, {'score': score}, user=user, xhr=True)

        ct = ContentType.objects.get_for_model(foo)

        self.assertTrue(UserRating.objects.filter(user=user, rating__object_id=foo.pk, rating__content_type=ct, score=score).exists())

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_request_is_ajax___response_is_updated_aggregate_data(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))

        response = self.post_json(
            url, {'score': score}, user=user, xhr=True)

        ratings = Rating.objects.get(pk=ratings.pk)
        expected = ratings.to_dict()
        expected['user_rating'] = score
        expected['percentage'] = float(expected['percentage'])

        try:
            json_resp = response.json()
        except AttributeError:
            json_resp = json.loads(response.content.decode())

        self.assertEqual(expected, json_resp)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___rating_is_updated(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        rating = mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        self.post_json(url, {'score': score}, user=user)

        rating = UserRating.objects.get(pk=rating.pk)

        self.assertEqual(score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___redirected_to_root(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___redirected_to_next(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true_request_is_ajax___rating_is_updated(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        rating = mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        self.post_json(url, {'score': score}, user=user, xhr=True)

        rating = UserRating.objects.get(pk=rating.pk)

        self.assertEqual(score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true_request_is_ajax___response_is_updated_aggregate_data(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))

        self.client.login(username=user.username, password='password')
        response = self.client.post(url, json.dumps({'score': score}), content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        response = self.post_json(url, {'score': score}, user=user, xhr=True)
        ratings = Rating.objects.get(pk=ratings.pk)
        expected = ratings.to_dict()
        expected['percentage'] = float(expected['percentage'])
        expected['user_rating'] = score

        try:
            json_resp = response.json()
        except AttributeError:
            json_resp = json.loads(response.content.decode())

        self.assertEqual(expected, json_resp)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false___rating_is_not_changed(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        rating = mommy.make(UserRating, rating=ratings, score=1, user=user)
        orig_score = rating.score

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        self.post_json(url, {'score': score}, user=user)

        rating = UserRating.objects.get(pk=rating.pk)

        self.assertEqual(orig_score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false___redirected_to_next(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false_request_is_ajax___rating_is_not_changed(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        rating = mommy.make(UserRating, rating=ratings, score=1, user=user)
        orig_score = rating.score

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        self.post_json(url, {'score': score}, user=user, xhr=True, expect_errors=True)

        rating = UserRating.objects.get(pk=rating.pk)
        self.assertEqual(orig_score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false_reuest_is_ajax___response_is_400(self):
        user = self.get_user()
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user, xhr=True, expect_errors=True)

        self.assertEqual(400, response.status_code)
