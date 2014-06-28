from django.conf.urls import patterns, url

from thewiki import views

urlpatterns = patterns('',
    url(r'^info$', views.index, name='index'),
    url(r'^pagelist/$', views.pagelist, name='pagelist'),
    url(r'^', views.disp_page, name='disp_page')
)

