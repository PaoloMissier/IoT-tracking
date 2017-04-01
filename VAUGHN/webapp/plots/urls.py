
from django.conf.urls import include, url
from django.http import HttpResponse
from django.shortcuts import render
import os
from django.conf import settings


from . import views

urlpatterns = [
    url(r'^$', views.plots, name='plots'),
]
