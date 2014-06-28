from django.conf.urls import patterns, url

from thewiki import views

urlpatterns = patterns('',
    url(r'^', views.default_page, name='default_page')
)

