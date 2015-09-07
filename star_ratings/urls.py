from django.conf.urls import patterns, url
from .views import RatingCreate


urlpatterns = patterns(
    '',
    url(r'(?P<pk>\d+)/(?P<score>\d+)/', RatingCreate.as_view(), name='rate'),
)
