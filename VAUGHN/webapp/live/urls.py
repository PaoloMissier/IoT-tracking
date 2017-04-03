
from django.conf.urls import url
from live import views

urlpatterns = [
    url(r'^$', views.live, name='live'),
    url(r'^log.txt$', views.file,name="log")
]
