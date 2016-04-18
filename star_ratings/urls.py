from django.conf.urls import patterns, url
from .views import Rate


urlpatterns = [
    url(r'(?P<content_type_id>\d+)/(?P<object_id>\d+)/', Rate.as_view(), name='rate'),
]
