from django.conf import settings


STAR_RATINGS_RANGE = getattr(settings, 'STAR_RATINGS_RANGE', 5)
STAR_RATINGS_ANONYMOUS = getattr(settings, 'STAR_RATINGS_ANONYMOUS', False)
