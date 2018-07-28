from django.conf.urls import url

import grouptb_app.views
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^list/$', views.list_current),
    url(r'^add/$', grouptb_app.views.add),
    url(r'^delete/$', grouptb_app.views.delete),
    url(r'^cloud-info/$', grouptb_app.views.cloud_info),
]
