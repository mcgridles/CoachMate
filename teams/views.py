# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import generic
from teams.models import Team, Swimmer

class TeamListView(generic.ListView):
    model = Team
    template_name = 'teams/team_list.html'

    def get_queryset(self):
        return Team.objects.order_by('name')

class SwimmerListView(generic.ListView):
    model = Swimmer
    template_name = 'teams/swimmer_list.html'

    def get_team_name(self):
        team = Team.objects.filter(pk=self.kwargs['abbr'])
        return team.name

    def get_queryset(self):
        team_name = get_team_name()
        return Swimmer.objects.filter(team=team_name)

class SwimmerDetailView(generic.DetailView):
    model = Swimmer
    template_name = 'teams/swimmer.html'

    def get_object(self):
        return Swimmer.objects.get(pk=self.kwargs['id'])
