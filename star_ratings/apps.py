from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save, post_delete


class StarRatingsAppConfig(AppConfig):
    name = 'star_ratings'

    def ready(self):
        from .models import UserRating, AnonymousRating
        from .signals import calculate_ratings

        if getattr(settings, 'STAR_RATINGS_ANONYMOUS', True) is False:
            post_save.connect(calculate_ratings, sender=UserRating)
            post_delete.connect(calculate_ratings, sender=UserRating)
        else:
            post_save.connect(calculate_ratings, sender=AnonymousRating)
            post_delete.connect(calculate_ratings, sender=AnonymousRating)
