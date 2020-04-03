from __future__ import unicode_literals

from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from .app.views import FooView, SizesView

urlpatterns = [
    path('', FooView.as_view(template_name='home.html'), name='home'),
    path('sizes', SizesView.as_view(), name='sizes'),
    path('', include(auth_urls)),
    path('admin/', admin.site.urls),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
]
