# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from teams.models import Team, Swimmer, Week, Practice, Set, Rep
from teams.forms import TeamForm, SwimmerForm, SetForm, PracticeForm, RepFormSet, RepInlineFormSet

@csrf_protect
@login_required
def teamList(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)

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


@login_required
def deleteTeam(request, abbr):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    team.delete()
    return redirect('teams:team_list')


@csrf_protect
@login_required
def swimmerList(request, abbr):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    if request.method == 'POST':
        form = SwimmerForm(request.POST)
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
        'team': team,
        'form': form,
        'swimmer_list': swimmer_list,
    }
    return render(request, 'teams/swimmer_list.html', context)


@login_required
def deleteSwimmer(request, abbr, pk):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    swimmer = Swimmer.objects.filter(team=team).get(pk=pk)
    swimmer.delete()
    return redirect('teams:swimmer_list', abbr=abbr)


@csrf_protect
@login_required
def writePractice(request, abbr, p_id):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    practice = Practice.objects.get(pk=p_id)
    if request.method == 'POST':
        setForm = SetForm(data=request.POST, p_id=p_id)
        rep_formset = RepFormSet(request.POST)

        if setForm.is_valid() and rep_formset.is_valid():
            setInstance = setForm.save(commit=False)
            setInstance.practice_id = Practice.objects.get(id=p_id)
            setInstance.save()

            rep_formset.save_formset(setInstance.id)

            setform = SetForm()
            rep_formset = RepFormSet()
            return redirect('teams:practice', abbr=team.abbr, p_id=p_id)

        else:
            set_list = Set.objects.filter(practice_id=p_id).order_by('order')
            context = {
                'team': team,
                'setForm': setForm,
                'rep_formset': rep_formset,
                'set_list': set_list,
            }
            return render(request, 'teams/practice_create.html', context)

    else:
        setForm = SetForm()
        rep_formset = RepFormSet()

    set_list = Set.objects.filter(practice_id=p_id).order_by('order')
    context = {
        'team': team,
        'practice': practice,
        'setForm': setForm,
        'rep_formset': rep_formset,
        'set_list': set_list,
    }
    return render(request, 'teams/practice_create.html', context)


@login_required
def deletePractice(request, abbr, p_id):
    practice = Practice.objects.get(pk=p_id)
    practice.delete()
    return redirect('teams:schedule', abbr=abbr)


@csrf_protect
@login_required
def practiceSchedule(request, abbr):
    team = Team.objects.filter(user=request.user).get(abbr=abbr)
    if request.method == 'POST':
        form = PracticeForm(request.POST)
        if form.is_valid():
            weekday = form.cleaned_data['weekday']
            if Practice.objects.filter(weekday=weekday):
                practices = Practice.objects.filter(weekday=weekday)
                practices.delete()

            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()

            context = {
                'team': team,
                'practice': instance
            }
            return redirect('teams:practice', abbr=team.abbr, p_id=instance.id)
    else:
        form = PracticeForm()

    try:
        practice_monday = Practice.objects.get(weekday='monday')
    except Practice.DoesNotExist:
        practice_monday = None
    try:
        practice_tuesday = Practice.objects.get(weekday='tuesday')
    except Practice.DoesNotExist:
        practice_tuesday = None
    try:
        practice_wednesday = Practice.objects.get(weekday='wednesday')
    except Practice.DoesNotExist:
        practice_wednesday = None
    try:
        practice_thursday = Practice.objects.get(weekday='thursday')
    except Practice.DoesNotExist:
        practice_thursday = None
    try:
        practice_friday = Practice.objects.get(weekday='friday')
    except Practice.DoesNotExist:
        practice_friday = None
    try:
        practice_saturday = Practice.objects.get(weekday='saturday')
    except Practice.DoesNotExist:
        practice_saturday = None
    try:
        practice_sunday = Practice.objects.get(weekday='sunday')
    except Practice.DoesNotExist:
        practice_sunday = None

    context = {
        'team': team,
        'form': form,
        'practice_monday': practice_monday,
        'practice_tuesday': practice_tuesday,
        'practice_wednesday': practice_wednesday,
        'practice_thursday': practice_thursday,
        'practice_friday': practice_friday,
        'practice_saturday': practice_saturday,
        'practice_sunday': practice_sunday,
    }

    return render(request, 'teams/practice_schedule.html', context)
