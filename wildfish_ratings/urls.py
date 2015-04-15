from django.conf.urls import patterns, url
from .views import RatingCreate


urlpatterns = patterns(
    '',
    url(r'', RatingCreate.as_view(), name='rate'),
)
