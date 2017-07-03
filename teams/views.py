# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User

from teams.models import Team, Swimmer, TeamForm, SwimmerForm

@csrf_protect
def teamList(request):
    if request.method == 'POST':
        form = TeamForm(data=request.POST)

        if form.is_valid():
            new_team = form.save(commit=False)
            new_team.user = request.user
            new_team.save()
            form = TeamForm()
    else:
        form = TeamForm()

    team_list = Team.objects.filter(user=request.user)
    context = {
        'form': form,
        'team_list': team_list,
    }
    return render(request, 'teams/team_list.html', context)

@csrf_protect
def swimmerList(request, abbr):
    team = Team.objects.get(abbr=abbr)
    if request.method == 'POST':
        form = SwimmerForm(data=request.POST)

        if form.is_valid():
            new_swimmer = form.save(commit=False)
            new_swimmer.team = team
            new_swimmer.save()
    else:
        form = SwimmerForm()

    swimmer_list  = team.swimmer_set.all()
    context = {
        'form': form,
        'swimmer_list': swimmer_list,
        'team': team,
    }
    return render(request, 'teams/swimmer_list.html', context)

class SwimmerDetailView(generic.DetailView):
    model = Swimmer
    template_name = 'teams/swimmer.html'

    def get_object(self):
        return Swimmer.objects.get(pk=self.kwargs['id'])
