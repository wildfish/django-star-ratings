from unittest import skip
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django_webtest import WebTest
from model_mommy import mommy
from ..models import Rating
from .models import Thing


User = get_user_model()


class RatingTests(WebTest):
    csrf_checks = False

    def setUp(self):
        self.thing_a = mommy.make(Thing)
        self.thing_b = mommy.make(Thing)
        self.thing_c = mommy.make(Thing)
        self.thing_content_type = ContentType.objects.get_for_model(Thing)
        self.user_a = mommy.make(User)
        self.user_b = mommy.make(User)

    def _rate(self, thing, user, score=3):
        post_data = {'object_id': thing.pk, 'content_type': ContentType.objects.get_for_model(Thing).pk, 'score': score}
        response = self.app.post(reverse('ratings:rate'), post_data, user=user)
        return response

    def test_rates_a(self):
        self._rate(self.thing_a, self.user_a)
        self._rate(self.thing_a, self.user_b)

        self.thing_a = Thing.objects.get(pk=self.thing_a.pk)

        self.assertEqual(self.thing_a.ratings.count(), 2)

    def test_rates_b(self):
        self._rate(self.thing_b, self.user_a)

        self.thing_b = Thing.objects.get(pk=self.thing_b.pk)

        self.assertEqual(self.thing_b.ratings.count(), 1)

    def test_cant_rate_twice(self):
        self._rate(self.thing_c, self.user_a)

        with self.assertRaises(IntegrityError):
            self._rate(self.thing_c, self.user_a)

    @skip('todo')  # TODO
    def test_unverified_cannot_rate(self):
        post_data = {'object_id': self.thing_c.pk, 'content_type_id': self.thing_content_type}
        self.app.post(reverse('ratings:create'), post_data, user=self.user_unverified, status=403)

    def test_has_rated(self):
        thing = mommy.make(Thing)
        user = mommy.make(User)

        self.assertFalse(Rating.objects.has_rated(user, thing))

        self._rate(thing, user)

        self.assertTrue(Rating.objects.has_rated(user, thing))
