from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('home.urls')),
    url(r'^home/', include('home.urls')),
    url(r'^plots/', include('plots.urls')),
    url(r'^live/', include('live.urls')),
]
