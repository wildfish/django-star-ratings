from __future__ import unicode_literals

from django.conf.urls import url, include

urlpatterns = [
    url(r'^ratings/', include('star_ratings.urls', namespace='ratings')),
]
