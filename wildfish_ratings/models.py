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
            if getattr(settings, 'WILDFISH_RATINGS_RERATE') is False:
                raise ValidationError('Already rated')
            rating.score = score
            rating.save()
        else:
            Rating.objects.create(user=user, score=score, ratable_model=instance, ip_address=ip_address)

        with transaction.atomic():
            instance = self.get(pk=instance.pk)
            instance.rating_count = Rating.objects.filter(ratable_model=instance).count()
            instance.rating_total = Rating.objects.filter(ratable_model=instance).aggregate(total_score=Sum('score')).get('total_score') or 0
            instance.save()
        return instance

    def has_rated(self, user, instance):
        return self.filter(pk=instance.pk, user=user).exists()


class RateableModel(models.Model):
    rating_count = models.PositiveIntegerField(default=0)
    rating_total = models.PositiveIntegerField(default=0)
    max_value = models.PositiveIntegerField()

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    objects = RateableModelManager()

    @property
    def rating_average(self):
        if self.rating_total is 0 or self.rating_count is 0:
            return 0
        return self.rating_total / self.rating_count


class Rating(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ip_address = models.IPAddressField(blank=True)  # TODO
    score = models.IntegerField()
    ratable_model = models.ForeignKey(RateableModel, related_name='ratings')

    class Meta:
        unique_together = ['user', 'ratable_model']

    def __str__(self):
        return 'User {} rating of {} for {}'.format(self.user_id, self.content_object)
