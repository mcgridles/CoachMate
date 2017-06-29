# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import generic
from teams.models import Team, Swimmer

def TeamListView(generic.ListView):
    model = Team
    template_name = teams/team_list.html

    def get_queryset(self):
        return Team.objects.order_by('name')

def SwimmerListView(generic.ListView):
    model = Swimmer
    template_name = teams/swimmer_list.html

    team = Team.objects.filter(pk=self.kwargs['abbr'])
    team_name = team.name

    def get_queryset(self):
        return Swimmer.objects.filter(team=team_name)

def SwimmerDetailView(generic.DetailView):
    model = Swimmer
    template_name = teams/swimmer.html

    def get_object(self):
        return Swimmer.objects.get(pk=self.kwargs['id'])
