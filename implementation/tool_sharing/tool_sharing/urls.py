"""tool_sharing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views
from user.views import sign_in, log_out


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^sign_in/$', sign_in, name="sign_in"),
    url(r'^log_out/$', log_out, name="log_out"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^manage_tools/', include('manage_tools.urls', namespace="manage_tools", app_name='manage_tools')),
    url(r'^account/', include('user.urls', namespace='user', app_name='user')),
    # the tool listing urls
    url(r'^tools/', include('tool_listing.urls', namespace='tool_listing', app_name='tool_listing')),
    # shed creating
    url(r'^shared_zone/', include('shared_zone.urls', namespace='shared_zone', app_name='shared_zone')),
    # the request urls
    url(r'^request/', include('request.urls', namespace='request', app_name='request')),

    # the request urls
    url(r'^statistics/', include('share_statistics.urls', namespace='share_statics', app_name='share_statistics')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
