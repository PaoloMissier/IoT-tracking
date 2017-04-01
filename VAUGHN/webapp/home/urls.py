from django.conf.urls import url
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    # url(r'^get/cubes/(?P<mints>=[\w-]+)&(?P<maxts>=[\w-]+)/$', views.cubes),
    url(r'^get/cubes/$', views.cubes, name='home'),
]

urlpatterns = format_suffix_patterns(urlpatterns)