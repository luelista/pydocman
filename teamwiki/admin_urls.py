from django.conf.urls import patterns, url
from django.contrib import admin
#from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url

admin.autodiscover()

urlpatterns = patterns('',
  url(r'^', include(admin.site.urls))

)
