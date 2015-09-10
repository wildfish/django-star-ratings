from __future__ import division
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
        aggregate, created = self.get_or_create(content_type=ct, object_id=instance.pk, defaults={'max_value': 5})
        existing_rating = Rating.objects.filter(aggregate__content_type=ct, user=user).first()
        if existing_rating:
            if getattr(settings, 'STAR_RATINGS_RERATE', True) is False:
                raise ValidationError('Already rated.')
            existing_rating.score = score
            existing_rating.save()
            return existing_rating.aggregate
        else:
            return Rating.objects.create(user=user, score=score, aggregate=aggregate, ip=ip).aggregate

    def has_rated(self, instance, user):
        if isinstance(instance, AggregateRating):
            raise Exception('AggregateRating manager expects model to be rated, not AggregateRating model.')
        return Rating.objects.filter(pk=instance.pk, user=user).exists()


@python_2_unicode_compatible
class AggregateRating(models.Model):
    """
    Attaches Rating models and running counts to the model being rated via a generic relation.
    """
    count = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    average = models.DecimalField(max_digits=6, decimal_places=3, default=0.0)
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
        return str(self.content_object)

    def calculate(self):
        """
        Recalculate the totals, and save.
        """
        aggregates = self.ratings.aggregate(total=Sum('score'), average=Avg('score'), count=Count('score'))
        self.count = aggregates.get('count') or 0
        self.total = aggregates.get('total') or 0
        self.average = aggregates.get('average') or 0.0
        self.save()


@python_2_unicode_compatible
class Rating(TimeStampedModel):
    """
    An individual rating of a user against a model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ip = models.GenericIPAddressField(blank=True, null=True)
    score = models.PositiveSmallIntegerField()
    aggregate = models.ForeignKey(AggregateRating, related_name='ratings')

    class Meta:
        unique_together = ['user', 'aggregate']

    def __str__(self):
        return 'User {} rating for {}'.format(self.user_id, self.aggregate)

    def save(self, *args, **kwargs):
        rating = super(Rating, self).save(*args, **kwargs)
        self.aggregate.calculate()
        return rating
