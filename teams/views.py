# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User

from teams.models import Team, Swimmer, TeamForm, SwimmerForm

@csrf_protect
def teamList(request):
    if request.method == 'POST':
        form = TeamForm(data=request.POST)

        if form.is_valid():
            try:
                team_name = form.cleaned_data['name']
                team = Team.objects.filter(user=request.user).get(name=team_name)
            except:
                new_team = form.save(commit=False)
                new_team.user = request.user
                new_team.save()
                return redirect('teams:team_list')
    else:
        form = TeamForm()

    team_list = Team.objects.filter(user=request.user)
    context = {
        'form': form,
        'team_list': team_list,
    }
    return render(request, 'teams/team_list.html', context)


def deleteTeam(request, abbr):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    team.delete()
    return redirect('teams:team_list')


@csrf_protect
def swimmerList(request, abbr):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    if request.method == 'POST':
        form = SwimmerForm(data=request.POST)
        if form.is_valid():
            last_name = form.cleaned_data['l_name']
            try:
                swimmer = Swimmer.objects.filter(team=team).get(l_name=last_name)
            except:
                new_swimmer = form.save(commit=False)
                new_swimmer.team = team
                new_swimmer.save()
                form = SwimmerForm()
                return redirect('teams:swimmer_list', abbr=team.abbr)
    else:
        form = SwimmerForm()

    swimmer_list  = team.swimmer_set.all()
    context = {
        'form': form,
        'swimmer_list': swimmer_list,
        'team': team,
    }
    return render(request, 'teams/swimmer_list.html', context)

def deleteSwimmer(request, abbr, pk):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    swimmer = Swimmer.objects.filter(team=team).get(pk=pk)
    swimmer.delete()
    return redirect('teams:swimmer_list', abbr=abbr)


class SwimmerDetailView(generic.DetailView):
    model = Swimmer
    template_name = 'teams/swimmer.html'

    def get_object(self):
        return Swimmer.objects.get(pk=self.kwargs['id'])

def practice(request, abbr):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    return render(request, 'teams/practice.html', {'team': team})
