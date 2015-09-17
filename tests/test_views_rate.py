import json
from random import randint
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import override_settings
from django_webtest import WebTest
from model_mommy import mommy
from star_ratings.models import Rating, UserRating
from .models import Foo


class ViewRate(WebTest):
    csrf_checks = False

    def post_json(self, url, data, **kwargs):
        return self.app.post(url, json.dumps(data), content_type='application/json', **kwargs)

    def test_view_is_called_when_nobody_is_logged_in___user_is_forwarded_to_login(self):
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.app.get(url)

        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url, fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_have_a_rating___rating_is_created(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        self.post_json(url, {'score': score}, user=user)

        ct = ContentType.objects.get_for_model(foo)
        self.assertTrue(UserRating.objects.filter(user=user, rating__object_id=foo.pk, rating__content_type=ct, score=score).exists())

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_no_next_url_is_given___redirected_to_root(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_next_url_is_given___redirected_to_next(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_request_is_ajax___rating_is_created(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))

        self.post_json(url, {'score': score}, user=user, xhr=True)

        ct = ContentType.objects.get_for_model(foo)
        self.assertTrue(UserRating.objects.filter(user=user, rating__object_id=foo.pk, rating__content_type=ct, score=score).exists())

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_request_is_ajax___response_is_updated_aggregate_data(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.post_json(url, {'score': score}, user=user, xhr=True)

        ratings = Rating.objects.get(pk=ratings.pk)
        expected = ratings.to_dict()
        expected['user_rating'] = score
        self.assertEqual(expected, response.json)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___rating_is_updated(self):
        user = mommy.make(get_user_model())
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
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___redirected_to_next(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true_request_is_ajax___rating_is_updated(self):
        user = mommy.make(get_user_model())
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
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id))
        response = self.post_json(url, {'score': score}, user=user, xhr=True)

        ratings = Rating.objects.get(pk=ratings.pk)
        expected = ratings.to_dict()
        expected['user_rating'] = score
        self.assertEqual(expected, response.json)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false___rating_is_not_changed(self):
        user = mommy.make(get_user_model())
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
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false_request_is_ajax___rating_is_not_changed(self):
        user = mommy.make(get_user_model())
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
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = Rating.objects.for_instance(foo)
        mommy.make(UserRating, rating=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.content_type_id, ratings.object_id)) + '?next=/foo/bar'
        response = self.post_json(url, {'score': score}, user=user, xhr=True, expect_errors=True)

        self.assertEqual(400, response.status_code)
