from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='tool_listing'),
    url(r'^(?P<id>[0-9]+)/$', views.tool_detail, name='tool_detail'),
]
