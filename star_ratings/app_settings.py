from django.conf import settings


STAR_RATINGS_RANGE = getattr(settings, 'STAR_RATINGS_RANGE', 5)
