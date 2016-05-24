from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^sign_up/$', views.sig_up, name="sign_up"),
    url(r'^my_profile/$', views.my_profile, name="my_profile"),
    url(r'^update_profile/$', views.update_profile, name="update_profile"),
    url(r'^change_password/$', views.change_password, name="change_password"),
    url(r'^pickup_arrangement/$', views.pickup_arrangement, name="pickup_arrangement"),
    url(r'^promote_coordinator/$', views.promote_coordinator, name="promote_coordinator"),
    url(r'^promote_coordinator/(?P<search_term>\w+)$', views.promote_coordinator, name="promote_coordinator"),
    url(r'^history/$', views.history, name="history"),
    url(r'^forgot_password/$', views.forgot_password, name="forgot_password"),
]