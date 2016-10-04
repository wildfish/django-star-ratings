from __future__ import unicode_literals

from django.conf.urls import url
from .views import Rate


urlpatterns = [
    url(r'(?P<content_type_id>\d+)/(?P<object_id>\d+)/', Rate.as_view(), name='rate'),
]
