from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^dailylog/$', views.dailylog),
    url(r'^districts-usage/$', views.districts_usage),
    url(r'^group/$', views.group),
    url(r'^group-tree/$', views.group_tree),
    url(r'^detaillog/$', views.detaillog),
]
