from django.conf import settings


class Settings:
    @property
    def STAR_RATINGS_RANGE(self):
        return getattr(settings, 'STAR_RATINGS_RANGE', 5)

    @property
    def STAR_RATINGS_ANONYMOUS(self):
        return getattr(settings, 'STAR_RATINGS_ANONYMOUS', False)

    @property
    def STAR_RATINGS_RERATE(self):
        return getattr(settings, 'STAR_RATINGS_RERATE', True)
