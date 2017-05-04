
from django.conf.urls import url
from live import views

urlpatterns = [
    url(r'^$', views.live, name='live')
]
