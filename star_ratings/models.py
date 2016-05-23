from __future__ import division
from decimal import Decimal
from warnings import warn
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Sum
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel
from .app_settings import STAR_RATINGS_RANGE, STAR_RATINGS_ANONYMOUS


class RatingManager(models.Manager):
    def for_instance(self, instance):
        if isinstance(instance, Rating):
            raise TypeError("Rating manager 'for_instance' expects model to be rated, not Rating model.")
        ct = ContentType.objects.get_for_model(instance)
        ratings, created = self.get_or_create(content_type=ct, object_id=instance.pk)
        return ratings

    def ratings_for_instance(self, instance):
        warn("RatingManager method 'for_instance' has been renamed to 'ratings_for_instance'. Please change uses of 'Rating.objects.ratings_for_instance' to 'Rating.objects.for_instance' in your code.", DeprecationWarning)
        return self.for_instance(instance)

    def rate(self, instance, score, user=None, ip=None):
        if isinstance(instance, Rating):
            raise TypeError("Rating manager 'rate' expects model to be rated, not Rating model.")
        ct = ContentType.objects.get_for_model(instance)
        
        if getattr(settings, 'STAR_RATINGS_ANONYMOUS', True) is False:
            if not user:
                raise ValidationError(_('User is mandatory!'))
            existing_rating = UserRating.objects.for_instance_by_user(instance, user)
        elif ip:
            existing_rating = AnonymousRating.objects.for_instance_by_anonymous(instance, ip)
        else:
            raise ValidationError(_('IP address is mandatory!'))
        
        if existing_rating:
            if getattr(settings, 'STAR_RATINGS_RERATE', True) is False:
                raise ValidationError(_('Already rated.'))
            existing_rating.score = score
            existing_rating.save()
            return existing_rating.rating
        else:
            rating, created = self.get_or_create(content_type=ct, object_id=instance.pk)
            if getattr(settings, 'STAR_RATINGS_ANONYMOUS', True) is False:
                return UserRating.objects.create(user=user, score=score, rating=rating, ip=ip).rating
            return AnonymousRating.objects.create(score=score, rating=rating, ip=ip).rating


@python_2_unicode_compatible
class Rating(models.Model):
    """
    Attaches Rating models and running counts to the model being rated via a generic relation.
    """
    count = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    average = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal(0.0))

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    objects = RatingManager()

    class Meta:
        unique_together = ['content_type', 'object_id']

    @property
    def percentage(self):
        return (self.average / STAR_RATINGS_RANGE) * 100

    def to_dict(self):
        return {
            'count': self.count,
            'total': self.total,
            'average': self.average,
            'percentage': self.percentage,
        }

    def __str__(self):
        return '{}'.format(self.content_object)

    def calculate(self):
        """
        Recalculate the totals, and save.
        """
        if getattr(settings, 'STAR_RATINGS_ANONYMOUS', True) is False:
            aggregates = self.user_ratings.aggregate(total=Sum('score'), average=Avg('score'), count=Count('score'))
        else:
            aggregates = self.anonymous_ratings.aggregate(total=Sum('score'), average=Avg('score'), count=Count('score'))
        self.count = aggregates.get('count') or 0
        self.total = aggregates.get('total') or 0
        self.average = aggregates.get('average') or 0.0
        self.save()


class UserRatingManager(models.Manager):
    def for_instance_by_user(self, instance, user):
        ct = ContentType.objects.get_for_model(instance)
        return self.filter(rating__content_type=ct, rating__object_id=instance.pk, user=user).first()

    def has_rated(self, instance, user):
        if isinstance(instance, Rating):
            raise TypeError("UserRating manager 'has_rated' expects model to be rated, not UserRating model.")
        rating = self.for_instance_by_user(instance, user)
        return rating is not None


@python_2_unicode_compatible
class UserRating(TimeStampedModel):
    """
    An individual rating of a user against a model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ip = models.GenericIPAddressField(blank=True, null=True)
    score = models.PositiveSmallIntegerField()
    rating = models.ForeignKey(Rating, related_name='user_ratings')

    objects = UserRatingManager()

    class Meta:
        unique_together = ['user', 'rating']

    def __str__(self):
        return '{} rating {} for {}'.format(self.user, self.score, self.rating.content_object)


class AnonymousRatingManager(models.Manager):
    def for_instance_by_anonymous(self, instance, ip):
        ct = ContentType.objects.get_for_model(instance)
        return self.filter(rating__content_type=ct, rating__object_id=instance.pk, ip=ip).first()

    def has_rated(self, instance, ip):
        if isinstance(instance, Rating):
            raise TypeError("AnonymousRating manager 'has_rated' expects model to be rated, not AnonymousRating model.")
        rating = self.for_instance_by_anonymous(instance, ip)
        return rating is not None


@python_2_unicode_compatible
class AnonymousRating(TimeStampedModel):
    """
    An anonymous rating against a model.
    """
    ip = models.GenericIPAddressField()
    score = models.PositiveSmallIntegerField()
    rating = models.ForeignKey(Rating, related_name='anonymous_ratings')

    objects = AnonymousRatingManager()

    class Meta:
        unique_together = ['ip', 'rating']

    def __str__(self):
        return '{} rating {} for {}'.format(self.ip, self.score, self.rating.content_object)
