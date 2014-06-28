from django.conf.urls import patterns, url, include

from dropmefiles import views, api

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', api.UserViewSet)
router.register(r'clipboards', api.ClipboardViewSet)
router.register(r'items', api.ItemViewSet)


urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^test1$', views.test1, name='test1'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    
    url(r'^list/$', views.list_clipboards, name='list_clipboards'),
    url(r'^\@([-\w0-9._]*)/([-\w0-9._]+)/$', views.show_clipboard, name='show_clipboard'),
    url(r'^\@([-\w0-9._]*)/([-\w0-9._]+)/([-\w0-9._]+)$', views.show_item, name='show_item'),
    url(r'^raw/([-\w0-9._]*)/([-\w0-9._]+)/([-\w0-9._]+)$', views.show_raw_item, name='show_raw_item'),
    url(r'^\@([-\w0-9._]*)/$', views.show_user, name='show_user'),
    
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    
    
)

