from django.conf.urls import patterns, url, include
from .views import RatingCreate


urlpatterns = patterns(
    '',
    url(r'(?P<pk>\d+)/(?P<rating_value>\d+)', RatingCreate.as_view(), name='rate'),
)
