from django.conf.urls import url, include

from stdb import admin
from .views import (
    IndexView,
    DetailView,
    list
)

app_name = 'stdb'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', DetailView.as_view(), name='detail'),
    url(r'^list/$', list, name='list'),
    ]