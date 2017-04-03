from django.conf.urls import url
from home import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^get/cubes/$', views.cubes, name='home'),
]
