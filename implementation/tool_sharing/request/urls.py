from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^sent/$', views.sent, name="sent"),
    url(r'^received/$', views.received, name="received"),
    url(r'^action/$', views.action, name="action"),
    url(r'^return_tool/(?P<pk>[0-9]+)/$', views.return_tool, name="return_tool"),
    url(r'^move_to_history/(?P<ac>[a-z]+)/(?P<pk>[0-9]+)/$', views.move_to_history, name="move_to_history"),
]