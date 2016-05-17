from django.conf.urls import url, include

from stdb import admin
from . import views

app_name = 'stdb'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    #url(r'^admin/', include(admin.site.urls) ),
    ]