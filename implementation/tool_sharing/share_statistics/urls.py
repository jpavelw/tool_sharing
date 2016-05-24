from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^community/$', views.community_statistics, name="community_statistics"),
    url(r'^individual/$', views.individual_statistics, name="individual_statistics"),
]