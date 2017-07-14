from django.conf.urls import url

from . import views

app_name = 'teams'
urlpatterns = [
    url(r'^$', views.teamList, name='team_list'),
    url(r'^(?P<abbr>\w+)/$', views.swimmerList, name='swimmer_list'),
    url(r'^(?P<abbr>\w+)/schedule/(?P<w_id>\d+)/$', views.practiceSchedule, name='schedule'),
    url(r'^(?P<abbr>\w+)/practice/(?P<p_id>\d+)/$', views.writePractice, name='practice'),
    url(r'^(?P<abbr>\w+)/team/delete/$', views.deleteTeam, name='deleteTeam'),
    url(r'^(?P<abbr>\w+)/swimmer/delete/(?P<s_id>\d+)/$', views.deleteSwimmer, name='deleteSwimmer'),
    url(r'^(?P<abbr>\w+)/practice/delete/(?P<p_id>\d+)/$', views.deletePractice, name='deletePractice'),
]
