from django.conf.urls import include, url
from django.contrib import admin

import grouptb_service.views

urlpatterns = [
    # Examples:
    # url(r'^$', 'grouptb_service.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', grouptb_service.views.index, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grouptb-old/', include('grouptb_app.urls', namespace='grouptb_app')),
    url(r'^grouptb/', include('grouptb_bs_app.urls', namespace='grouptb_bs_app')),
    url(r'^upyun/', include('upyun_app.urls', namespace='upyun_app')),
    url(r'^upyun-bs/', include('upyun_bs_app.urls', namespace='upyun_bs_app')),
]
