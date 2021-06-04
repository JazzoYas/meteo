from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^getchart/$', views.getchart, name='getchart'),
    url(r'^getchart2/$', views.getchart2, name='getchart2')
]
