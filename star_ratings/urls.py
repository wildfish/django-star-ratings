from django.conf.urls import patterns, url
from .views import Rate


urlpatterns = patterns(
    '',
    url(r'(?P<pk>\d+)/(?P<score>\d+)/', Rate.as_view(), name='rate'),
)
