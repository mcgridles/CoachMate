from django.conf.urls import url

from . import views

app_name = 'accounts'
urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^settings/$', views.settings, name='settings'),
]
