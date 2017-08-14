from django.conf.urls import url

from . import views

app_name = 'teams'
urlpatterns = [
    # Dashboard
    url(r'^$', views.teamList, name='teamList'),

    # Training views
    url(r'^train/$', views.showTraining, name='showTraining'),
    url(r'^train/create/(?P<t_id>\d+)/$', views.createTraining, name='createTraining'),
    url(r'^train/delete/(?P<t_id>\d+)/$', views.deleteTraining, name='deleteTraining'),

    # Team specific views
    url(r'^(?P<abbr>\w+)/$', views.swimmerList, name='swimmerList'),
    url(r'^(?P<abbr>\w+)/(?P<s_id>\d+)/$', views.swimmerDetail, name='swimmerDetail'),
    url(r'^(?P<abbr>\w+)/schedule/(?P<w_id>\d+)/$', views.practiceSchedule, name='practiceSchedule'),
    url(r'^(?P<abbr>\w+)/practice/(?P<p_id>\d+)/$', views.writePractice, name='writePractice'),
    url(r'^(?P<abbr>\w+)/records/$', views.teamRecords, name='teamRecords'),

    # Delete models
    url(r'^(?P<abbr>\w+)/team/delete/$', views.deleteTeam, name='deleteTeam'),
    url(r'^(?P<abbr>\w+)/swimmer/delete/(?P<s_id>\d+)/$', views.deleteSwimmer, name='deleteSwimmer'),
    url(r'^(?P<abbr>\w+)/practice/delete/(?P<p_id>\d+)/$', views.deletePractice, name='deletePractice'),
    url(r'^(?P<abbr>\w+)/set/delete/(?P<set_id>\d+)/$', views.deleteSet, name='deleteSet'),
]
