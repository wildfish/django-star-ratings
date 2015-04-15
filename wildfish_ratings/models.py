from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from model_utils.models import TimeStampedModel


class RatingManager(models.Manager):
    def count_for_entry(self, entry):
        return self.filter(entry_media__entry=entry).count()

    def for_entry_by_user(self, entry, user):
        return self.filter(entry_media__entry=entry, user=user)

    def by_user(self, user):
        return self.filter(user=user)

    def has_rated(self, user, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        return self.by_user(user).filter(content_type=content_type, object_id=content_object.pk).exists()


class Rating(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    content_type = models.ForeignKey(ContentType, related_name='ratings')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    ip_address = models.IPAddressField(blank=True)  # TODO

    score = models.IntegerField()

    objects = RatingManager()

    class Meta:
        unique_together = ['user', 'content_type', 'object_id', ]

    def __str__(self):
        return 'User {} rating of {} for {}'.format(self.user_id, self.content_object)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # recalculate the denormalised vote count
        # may need to change this to an incremented count where we know it's a
        # new vote...
        # self.entry_media.entry.update_vote_count(self.entry_media.entry.pk)


class RateableModel(models.Model):
    """
    Mixin for a ratable model. #TODO - spelling/naming
    """
    ratings = GenericRelation(Rating)
    rating_count = models.PositiveIntegerField(default=0)
    rating_total = models.PositiveIntegerField(default=0)
    rating_average = models.FloatField(default=0)

    class Meta:
        abstract = True
