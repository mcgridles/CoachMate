from django.conf.urls import url

from . import views

app_name = 'teams'
urlpatterns = [
    url(r'^$', views.teamList, name='team_list'),
    url(r'^(?P<abbr>\w+)/$', views.swimmerList, name='swimmer_list'),
    url(r'^(?P<abbr>\w+)/(?P<id>[0-9]+)/$', views.SwimmerDetailView.as_view(), name='swimmer'),
    url(r'^(?P<abbr>\w+)/practice/$', views.practice, name='practice'),
    url(r'^(?P<abbr>\w+)/delete/$', views.deleteTeam, name='deleteTeam'),
    url(r'^(?P<abbr>\w+)/(?P<pk>[0-9]+)/delete/$', views.deleteSwimmer, name='deleteSwimmer'),
]
