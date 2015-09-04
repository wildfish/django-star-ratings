from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from model_utils.models import TimeStampedModel


class RateableModelManager(models.Manager):
    def ratings_for_item(self, item, max_value=5):
        ct = ContentType.objects.get_for_model(item)
        rateable = self.filter(content_type=ct, object_id=item.pk).first()
        if rateable:
            return rateable
        return self.create(content_type=ct, object_id=item.pk, max_value=max_value)

    def rate(self, instance, score, user, ip_address):
        if not user.is_active:
            raise ValidationError('User is not active')

        rating = Rating.objects.filter(user=user, ratable_model=instance).first()
        if rating:
            if getattr(settings, 'WILDFISH_RATINGS_RERATE', True) is False:
                raise ValidationError('Already rated')
            rating.score = score
            rating.save()
            return rating.ratable_model
        else:
            return Rating.objects.create(user=user, score=score, ratable_model=instance, ip_address=ip_address).ratable_model

    def has_rated(self, instance, user):
        return Rating.objects.filter(pk=instance.pk, user=user).exists()


class RateableModel(models.Model):
    """
    Attaches Rating models and running counts to the model being rated via a generic relation.
    """
    rating_count = models.PositiveIntegerField(default=0)
    rating_total = models.PositiveIntegerField(default=0)
    rating_average = models.PositiveIntegerField(default=0)
    max_value = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    objects = RateableModelManager()

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
    An individual rating of a user against a RateableModel.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ip_address = models.IPAddressField(blank=True)  # TODO
    score = models.IntegerField()
    ratable_model = models.ForeignKey(RateableModel, related_name='ratings')

    class Meta:
        unique_together = ['user', 'ratable_model']

    def __str__(self):
        return 'User {} rating for {}'.format(self.user_id, self.ratable_model)

    def save(self, *args, **kwargs):
        res = super(Rating, self).save(*args, **kwargs)

        with transaction.atomic():
            self.ratable_model.rating_count = Rating.objects.filter(ratable_model=self.ratable_model).count()
            self.ratable_model.rating_total = Rating.objects.filter(ratable_model=self.ratable_model).aggregate(total_score=Sum('score')).get('total_score') or 0
            self.ratable_model.rating_average = float(self.ratable_model.rating_total) / self.ratable_model.rating_count
            self.ratable_model.save()

        return res
