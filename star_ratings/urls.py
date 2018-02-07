from __future__ import unicode_literals

from django.conf.urls import url

from .views import Rate
from . import app_settings


urlpatterns = [
    url(r'(?P<content_type_id>\d+)/(?P<object_id>' + app_settings.STAR_RATINGS_OBJECT_ID_PATTERN + ')/', Rate.as_view(), name='rate'),
]

app_name = 'star_ratings'
