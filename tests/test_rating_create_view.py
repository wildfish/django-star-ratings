from random import randint
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from model_mommy import mommy
from django_webtest import WebTest
from django.test import override_settings
from .models import Foo
from star_ratings.models import AggregateRating, Rating


class RatingCreateView(WebTest):
    csrf_checks = False

    def test_view_is_called_when_nobody_is_logged_in___user_is_forwarded_to_login(self):
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)

        url = reverse('ratings:rate', args=(ratings.pk, 3))
        response = self.app.get(url)

        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url, fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_have_a_rating___rating_is_created(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        self.app.post(url, user=user)

        ct = ContentType.objects.get_for_model(foo)
        self.assertTrue(Rating.objects.filter(user=user, aggregate__object_id=foo.pk, aggregate__content_type=ct, score=score).exists())

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_no_next_url_is_given___redirected_to_root(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        response = self.app.post(url, user=user)

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_have_a_rating_next_url_is_given___redirected_to_next(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score)) + '?next=/foo/bar'
        response = self.app.post(url, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    def test_user_is_logged_in_and_doesnt_already_request_is_ajax___rating_is_created(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        self.app.post(url, user=user, xhr=True)

        ct = ContentType.objects.get_for_model(foo)
        self.assertTrue(Rating.objects.filter(user=user, aggregate__object_id=foo.pk, aggregate__content_type=ct, score=score).exists())

    def test_user_is_logged_in_and_doesnt_already_request_is_ajax___response_is_updated_aggregate_data(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)

        score = randint(1, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        response = self.app.post(url, user=user, xhr=True)

        ratings = AggregateRating.objects.get(pk=ratings.pk)
        self.assertEqual(ratings.to_dict(), response.json)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___rating_is_updated(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        rating = mommy.make(Rating, aggregate=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        self.app.post(url, user=user)

        rating = Rating.objects.get(pk=rating.pk)
        self.assertEqual(score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___redirected_to_root(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        mommy.make(Rating, aggregate=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        response = self.app.post(url, user=user)

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true___redirected_to_next(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        mommy.make(Rating, aggregate=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score)) + '?next=/foo/bar'
        response = self.app.post(url, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true_request_is_ajax___rating_is_updated(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        rating = mommy.make(Rating, aggregate=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        self.app.post(url, user=user, xhr=True)

        rating = Rating.objects.get(pk=rating.pk)
        self.assertEqual(score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_true_request_is_ajax___response_is_updated_aggregate_data(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        mommy.make(Rating, aggregate=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        response = self.app.post(url, user=user, xhr=True)

        ratings = AggregateRating.objects.get(pk=ratings.pk)
        self.assertEqual(ratings.to_dict(), response.json)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false___rating_is_not_changed(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        rating = mommy.make(Rating, aggregate=ratings, score=1, user=user)
        orig_score = rating.score

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        self.app.post(url, user=user)

        rating = Rating.objects.get(pk=rating.pk)
        self.assertEqual(orig_score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false___redirected_to_next(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        mommy.make(Rating, aggregate=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score)) + '?next=/foo/bar'
        response = self.app.post(url, user=user)

        self.assertRedirects(response, '/foo/bar', fetch_redirect_response=False)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false_request_is_ajax___rating_is_not_changed(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        rating = mommy.make(Rating, aggregate=ratings, score=1, user=user)
        orig_score = rating.score

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score))
        self.app.post(url, user=user, xhr=True, expect_errors=True)

        rating = Rating.objects.get(pk=rating.pk)
        self.assertEqual(orig_score, rating.score)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_user_is_logged_in_already_has_a_rating_rerate_is_false_reuest_is_ajax___response_is_400(self):
        user = mommy.make(get_user_model())
        foo = mommy.make(Foo)
        ratings = AggregateRating.objects.ratings_for_item(foo)
        mommy.make(Rating, aggregate=ratings, score=1, user=user)

        score = randint(2, 5)

        url = reverse('ratings:rate', args=(ratings.pk, score)) + '?next=/foo/bar'
        response = self.app.post(url, user=user, xhr=True, expect_errors=True)

        self.assertEqual(400, response.status_code)
