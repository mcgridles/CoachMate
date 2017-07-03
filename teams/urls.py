from django.conf.urls import url

from . import views

app_name = 'teams'
urlpatterns = [
    url(r'^$', views.teamList, name='team_list'),
    url(r'^(?P<abbr>\w+)/$', views.swimmerList, name='swimmer_list'),
    url(r'^(?P<abbr>\w+)/(?P<id>[0-9]+)/$', views.SwimmerDetailView.as_view(), name='swimmer'),
]
