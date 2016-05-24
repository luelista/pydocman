"""docman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from dropme import views as dropme_views

urlpatterns = [
    url(r'^accounts/profile/$', dropme_views.myprofile, name="my_profile"),
    url(r'^admin/', admin.site.urls),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^activity/', include('actstream.urls')),

    url(r'^$', dropme_views.homepage, name="homepage"),
    url(r'^dashboard$', dropme_views.dashboard, name="dashboard"),
    url(r'^u/(?P<username>[\w.-]+)/$', dropme_views.userprofile, name="user_profile"),
    url(r'clipboards/create/', dropme_views.create_clipboard, name="create_clipboard"),
    url(r'^item/preview_image/(?P<doc_id>[\d]+)/(?P<size>[\d]+)$', dropme_views.file_preview,
        name="file_preview"),
    url(r'^item/preview_image/(?P<doc_id>[\d]+)/(?P<size>[\d]+)/(?P<page>[\d]+)$', dropme_views.file_preview,
        name="file_preview"),

    url(r'^documents/raw/(?P<doc_id>[\w.-]+)/$', dropme_views.file_raw, name="file_raw"),
    url(r'(?P<token>[\w-]{9})/(?P<slug>[\w-]+)/', dropme_views.show_clipboard, name="show_clipboard"),
    url(r'(?P<token>[\w-]{9})/(?P<slug>[\w-]+)/(?P<url_filename>[\w-]+)', dropme_views.show_document, name="show_document"),
    url(r'(?P<readonly_token>[\w-]{12})', dropme_views.show_document, name="show_document"),

]
