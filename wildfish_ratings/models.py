from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from model_utils.models import TimeStampedModel


class AggregateRatingManager(models.Manager):
    def ratings_for_item(self, item, max_value=5):
        ct = ContentType.objects.get_for_model(item)
        aggregate = self.filter(content_type=ct, object_id=item.pk).first()
        if aggregate:
            return aggregate
        return self.create(content_type=ct, object_id=item.pk, max_value=max_value)

    def rate(self, instance, score, user, ip_address):
        if not user.is_active:
            raise ValidationError('User is not active')

        rating = Rating.objects.filter(user=user, aggregate=instance).first()
        if rating:
            if getattr(settings, 'WILDFISH_RATINGS_RERATE', True) is False:
                raise ValidationError('Already rated')
            rating.score = score
            rating.save()
            return rating.aggregate
        else:
            return Rating.objects.create(user=user, score=score, aggregate=instance, ip_address=ip_address).aggregate

    def has_rated(self, instance, user):
        return Rating.objects.filter(pk=instance.pk, user=user).exists()


class AggregateRating(models.Model):
    """
    Attaches Rating models and running counts to the model being rated via a generic relation.
    """
    rating_count = models.PositiveIntegerField(default=0)
    rating_total = models.PositiveIntegerField(default=0)
    rating_average = models.FloatField(default=0.0)
    max_value = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    objects = AggregateRatingManager()

    def to_dict(self):
        return {
            'rating_count': self.rating_count,
            'rating_total': self.rating_total,
            'rating_average': self.rating_average,
            'max_value': self.max_value
        }

    def __str__(self):
        return str(self.content_object)


class Rating(TimeStampedModel):
    """
    An individual rating of a user against a model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ip_address = models.IPAddressField(blank=True)  # TODO
    score = models.IntegerField()
    aggregate = models.ForeignKey(AggregateRating, related_name='ratings')

    class Meta:
        unique_together = ['user', 'aggregate']

    def __str__(self):
        return 'User {} rating for {}'.format(self.user_id, self.ratable_model)

    def save(self, *args, **kwargs):
        res = super(Rating, self).save(*args, **kwargs)

        with transaction.atomic():
            self.aggregate.rating_count = Rating.objects.filter(aggregate=self.aggregate).count()
            self.aggregate.rating_total = Rating.objects.filter(aggregate=self.aggregate).aggregate(total_score=Sum('score')).get('total_score') or 0
            self.aggregate.rating_average = float(self.aggregate.rating_total) / self.aggregate.rating_count
            self.aggregate.save()

        return res
