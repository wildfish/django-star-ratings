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


class AggregateRatingManager(models.Manager):
    def ratings_for_model(self, item, max_value=5):
        ct = ContentType.objects.get_for_model(item)
        aggregate, created = self.get_or_create(content_type=ct, object_id=item.pk, defaults={'max_value': max_value})
        return aggregate

    def rate(self, instance, score, user, ip=None):
        if isinstance(instance, AggregateRating):
            raise Exception('AggregateRating manager expects model to be rated, not AggregateRating model.')
        ct = ContentType.objects.get_for_model(instance)
        existing_rating = Rating.objects.for_instance_by_user(instance, user)
        if existing_rating:
            if getattr(settings, 'STAR_RATINGS_RERATE', True) is False:
                raise ValidationError('Already rated.')
            existing_rating.score = score
            existing_rating.save()
            return existing_rating.aggregate
        else:
            aggregate, created = self.get_or_create(content_type=ct, object_id=instance.pk, defaults={'max_value': 5})
            return Rating.objects.create(user=user, score=score, aggregate=aggregate, ip=ip).aggregate


@python_2_unicode_compatible
class AggregateRating(models.Model):
    """
    Attaches Rating models and running counts to the model being rated via a generic relation.
    """
    count = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    average = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal(0.0))
    max_value = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    objects = AggregateRatingManager()

    class Meta:
        unique_together = ['content_type', 'object_id']

    def to_dict(self):
        return {
            'count': self.count,
            'total': self.total,
            'average': self.average,
            'max_value': self.max_value
        }

    def __str__(self):
        return '{}'.format(self.content_object)

    def calculate(self):
        """
        Recalculate the totals, and save.
        """
        aggregates = self.ratings.aggregate(total=Sum('score'), average=Avg('score'), count=Count('score'))
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
            raise Exception('Rating manager has_rated expects model to be rated, not AggregateRating model.')
        rating = self.for_instance_by_user(instance, user)
        return rating is not None


@python_2_unicode_compatible
class Rating(TimeStampedModel):
    """
    An individual rating of a user against a model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ip = models.GenericIPAddressField(blank=True, null=True)
    score = models.PositiveSmallIntegerField()
    aggregate = models.ForeignKey(AggregateRating, related_name='ratings')

    objects = RatingManager()

    class Meta:
        unique_together = ['user', 'aggregate']

    def __str__(self):
        return '{} rating {} for {}'.format(self.user, self.score, self.aggregate.content_object)

    def save(self, *args, **kwargs):
        rating = super(Rating, self).save(*args, **kwargs)
        self.aggregate.calculate()
        return rating
