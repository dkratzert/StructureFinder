from django.conf.urls import url
from django.conf import settings

from .views import (
    index_view,
    detail_view,
    list,
    edit_dataset,
    delete_dataset,
    new_dataset,
    )

app_name = 'stdb'
urlpatterns = [
    url(r'^$', index_view, name='index'),
    url(r'^(?P<pk>\d+)/$', detail_view, name='detail'),
    url(r'^(?P<pk>\d+)/edit/$', edit_dataset, name='edit'),
    url(r'^(?P<pk>\d+)/delete/$', delete_dataset, name='delete'),
    url(r'^new/$', new_dataset, name='new'),
    url(r'^list/$', list, name='list'),
    ]

"""
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
"""