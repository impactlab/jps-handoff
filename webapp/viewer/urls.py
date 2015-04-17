from django.conf.urls import patterns, url
from viewer import views

urlpatterns = patterns('',
        url(r'^$', views.home, name='home'),
        url(r'^summary/download$', views.download_summary, name='download_summary'),
        url(r'^meter/(?P<id>\d+)/download$', views.download_meter, name='download_meter'),
        url(r'^meter/(?P<id>\d+)/$', views.meter_detail, name='meter_detail'),
        url(r'^auditlist/clear$', views.clear_auditlist, name='clear_auditlist'),
        url(r'^auditlist/download$', views.download_auditlist, name='download_auditlist'),
        url(r'^auditlist/$', views.auditlist, name='auditlist'),
        url(r'^api/get_groups/', views.get_groups, name='get_groups'),
        )
