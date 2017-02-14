from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^home/', include('home.urls')),
    url(r'^live/', include('live.urls')),
    url(r'^admin/', admin.site.urls),
]
