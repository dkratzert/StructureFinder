from django.conf.urls import url, include

from stdb import admin
from .views import (
    index_view,
    detail_view,
    list
)

#app_name = 'stdb'
urlpatterns = [
    url(r'^$', index_view, name='index'),
    url('^(?P<pk>\d+)/$', detail_view, name='detail'),
    url(r'^list/$', list, name='list'),
    ]