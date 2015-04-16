from django.conf.urls import patterns, include, url
from django.contrib import admin
from .app.views import FooView


urlpatterns = patterns('',
    url(r'^$', FooView.as_view(template_name='home.html'), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ratings/', include('wildfish_ratings.urls', namespace='ratings', app_name='ratings')),
)
