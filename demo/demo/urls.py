from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from .app.views import FooView, SizesView

urlpatterns = patterns('',
    url(r'^$', FooView.as_view(template_name='home.html'), name='home'),
    url(r'^sizes$', SizesView.as_view(), name='sizes'),
    url(r'^', include(auth_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ratings/', include('star_ratings.urls', namespace='ratings', app_name='ratings')),
)
