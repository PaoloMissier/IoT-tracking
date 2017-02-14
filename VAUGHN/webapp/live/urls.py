
from django.conf.urls import include, url
from django.http import HttpResponse
from django.shortcuts import render
import os
from django.conf import settings


from . import views

urlpatterns = [
    url(r'^$', views.live, name='live'),
    url(r'^log.txt$', views.file ,name="log")
]
