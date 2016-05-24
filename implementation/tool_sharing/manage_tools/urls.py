from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^review_review/(?P<pk>[0-9]+)/$', views.review_review, name="review_review"),
    url(r'^my_tools/$', views.my_tools, name="my_tools"),
    url(r'^new_tool/$', views.new_tool, name="new_tool"),
    url(r'^get_reviews/(?P<pk>[0-9]+)/$', views.get_reviews, name="get_reviews"),
    url(r'^post_review/(?P<pk>[0-9]+)/$', views.post_review, name="post_review"),
    url(r'^edit_tool/(?P<pk>[0-9]+)/$', views.edit_tool, name="edit_tool"),
    url(r'^remove_tool/(?P<pk>[0-9]+)/$', views.remove_tool, name="remove_tool"),
    url(r'^update_status/(?P<pk>[0-9]+)/$', views.update_status, name="update_status"),
    url(r'^available_reviews/$', views.available_reviews, name="available_reviews"),
]
