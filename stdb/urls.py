from django.conf.urls import url

from stdb import admin
from .views import (
    index_view,
    detail_view,
    list,
    dataset_create,
    dataset_update,
)

#app_name = 'stdb'
urlpatterns = [
    url(r'^$', index_view, name='index'),
    url(r'^(?P<pk>\d+)/$', detail_view, name='detail'),
    url(r'^(?P<pk>\d+)/edit/$', dataset_update, name='update'),
    url(r'^new/$', dataset_create, name='new'),
    url(r'^list/$', list, name='list'),
    ]