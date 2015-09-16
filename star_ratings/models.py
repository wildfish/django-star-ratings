from __future__ import division
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Sum
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
from .app_settings import STAR_RATINGS_RANGE


class AggregateRatingManager(models.Manager):
    def ratings_for_instance(self, instance):
        if isinstance(instance, AggregateRating):
            raise TypeError("AggregateRating manager 'ratings_for_model' expects model to be rated, not AggregateRating model.")
        ct = ContentType.objects.get_for_model(instance)
        aggregate, created = self.get_or_create(content_type=ct, object_id=instance.pk)
        return aggregate

    def rate(self, instance, score, user, ip=None):
        if isinstance(instance, AggregateRating):
            raise TypeError("AggregateRating manager 'rate' expects model to be rated, not AggregateRating model.")
        ct = ContentType.objects.get_for_model(instance)
        existing_rating = UserRating.objects.for_instance_by_user(instance, user)
        if existing_rating:
            if getattr(settings, 'STAR_RATINGS_RERATE', True) is False:
                raise ValidationError('Already rated.')
            existing_rating.score = score
            existing_rating.save()
            return existing_rating.aggregate
        else:
            aggregate, created = self.get_or_create(content_type=ct, object_id=instance.pk)
            return UserRating.objects.create(user=user, score=score, aggregate=aggregate, ip=ip).aggregate


@python_2_unicode_compatible
class AggregateRating(models.Model):
    """
    Attaches Rating models and running counts to the model being rated via a generic relation.
    """
    count = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    average = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal(0.0))

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    objects = AggregateRatingManager()

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
        aggregates = self.user_ratings.aggregate(total=Sum('score'), average=Avg('score'), count=Count('score'))
        self.count = aggregates.get('count') or 0
        self.total = aggregates.get('total') or 0
        self.average = aggregates.get('average') or 0.0
        self.save()


class RatingManager(models.Manager):
    def for_instance_by_user(self, instance, user):
        ct = ContentType.objects.get_for_model(instance)
        return self.filter(aggregate__content_type=ct, aggregate__object_id=instance.pk, user=user).first()

    def has_rated(self, instance, user):
        if isinstance(instance, AggregateRating):
            raise TypeError("Rating manager 'has_rated' expects model to be rated, not AggregateRating model.")
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
    aggregate = models.ForeignKey(AggregateRating, related_name='user_ratings')

    objects = RatingManager()

    class Meta:
        unique_together = ['user', 'aggregate']

    def __str__(self):
        return '{} rating {} for {}'.format(self.user, self.score, self.aggregate.content_object)
