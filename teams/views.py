# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core import serializers

from teams.models import *
from teams.forms import *
import teams.functions as funct

@csrf_protect
@login_required
def teamList(request):
    if request.method == 'POST':
        form = TeamForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                # do nothing if team already exists
                team_name = form.cleaned_data['name']
                team = Team.objects.filter(user=request.user).get(name=team_name)
            except:
                # else create new team
                form.save()
                form = TeamForm(user=request.user)
                return redirect('teams:team_list')
    else:
        form = TeamForm()

    team_list = Team.objects.filter(user=request.user).order_by('name')
    context = {
        'form': form,
        'team_list': team_list,
    }
    return render(request, 'teams/team_list.html', context)


# Delete a team
@login_required
def deleteTeam(request, abbr):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    team.delete()
    return redirect('teams:team_list')


@csrf_protect
@login_required
def swimmerList(request, abbr):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    if request.method == 'POST':
        form = SwimmerForm(request.POST, team=team)
        if form.is_valid():
            last_name = form.cleaned_data['l_name']
            first_name = form.cleaned_data['f_name']
            try:
                # do nothing if swimmer already exists
                swimmer = Swimmer.objects.filter(team=team).filter(
                    l_name=last_name).get(f_name=first_name)
            except:
                # else create new swimmer
                new_swimmer = form.save()
                form = SwimmerForm()
                return redirect('teams:swimmer_list', abbr=team.abbr)
    else:
        form = SwimmerForm()

    swimmer_list  = Swimmer.objects.filter(team=team).order_by('l_name')
    context = {
        'team': team,
        'form': form,
        'swimmer_list': swimmer_list,
    }
    return render(request, 'teams/swimmer_list.html', context)


# Delete a swimmer
@login_required
def deleteSwimmer(request, abbr, s_id):
    swimmer = get_object_or_404(Swimmer, pk=s_id)
    swimmer.delete()
    return redirect('teams:swimmer_list', abbr=abbr)


@csrf_protect
@login_required
def writePractice(request, abbr, p_id):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    practice = get_object_or_404(Practice, Q(team=team), pk=p_id)
    if request.method == 'POST':
        setForm = SetForm(data=request.POST, practice=practice)
        rep_formset = RepFormSet(request.POST)
        if setForm.is_valid() and rep_formset.is_valid():
            # delete any other practices created on weekday for given team/week
            # currently there should never be more than one practice per day
            # checking now instead of when the practice is created means the
            # previous practice is not lost until this one is populated with sets
            if Practice.objects.filter(team=team).filter(
                week_id=practice.week_id).filter(
                weekday=practice.weekday).exclude(pk=practice.id):
                practice_list = Practice.objects.filter(team=team).filter(
                    week_id=practice.week_id).filter(
                    weekday=practice.weekday).exclude(pk=practice.id)
                for p in practice_list:
                    p.delete()

            # get set form instance
            setInstance = setForm.save()
            rep_formset.save_formset(setInstance) # set set_id for each rep

            setform = SetForm()
            rep_formset = RepFormSet()
            return redirect('teams:practice', abbr=team.abbr, p_id=p_id)

        else:
            # display errors
            set_list = Set.objects.filter(practice_id=p_id).order_by('order')
            context = {
                'team': team,
                'practice': practice,
                'week': practice.week_id.id,
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
        'week': practice.week_id.id,
        'setForm': setForm,
        'rep_formset': rep_formset,
        'set_list': set_list,
    }
    return render(request, 'teams/practice_create.html', context)


# Delete a practice
@login_required
def deletePractice(request, abbr, p_id):
    practice = get_object_or_404(Practice, pk=p_id)
    w_id = practice.week_id.id
    practice.delete()
    return redirect('teams:schedule', abbr=abbr, w_id=w_id)


@csrf_protect
@login_required
def practiceSchedule(request, abbr, w_id):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    weeks = {
        'current_week': None,
        'previous_week': 0,
        'next_week': 1,
    }
    # loop through current, next, and previous weeks
    for key in sorted(weeks):
        flag = False
        try:
            # try database queries
            if int(w_id) is 0 and 'current_week' in key:
                # w_id = 0 if requesting the current week
                flag = True
                funct.check_present() # check weeks for current
                weeks[key] = Week.objects.get(present=True)
            elif int(w_id) is not 0 and 'current_week' in key:
                # get week with id w_id as 'current week'
                weeks[key] = Week.objects.get(id=w_id)
            else:
                # get next and previous weeks (for next/previous buttons)
                weeks[key] = weeks['current_week'].get_week(weeks[key])
        except Week.DoesNotExist:
            # else create week
            if not flag: # return date of necessary Monday
                monday = funct.get_monday(weeks['current_week'], weeks[key])
            else:
                monday = funct.get_monday(weeks[key])
            weeks[key] = Week.objects.create(monday=monday, present=flag)
            weeks[key].populate() # populate dates for rest of week

    if request.method == 'POST':
        form = PracticeForm(request.POST, team=team, week=weeks['current_week'])
        if form.is_valid():
            # create new practice with no sets
            # allows new sets to be associated with a practice
            practice = form.save()

            context = {
                'team': team,
                'practice': practice,
            }
            return redirect('teams:practice', abbr=team.abbr, p_id=practice.id)
    else:
        form = PracticeForm()

    practices = []
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ,'sunday']
    for day in weekdays:
        # create list of practices
        try:
            practices.append(Practice.objects.filter(team=team).filter(
                week_id=weeks['current_week']).order_by('order').get(weekday=day))
        except Practice.DoesNotExist:
            practices.append(None)

    practices = zip(practices, weekdays) # add weekdays
    dates = Week.objects.filter(pk=weeks['current_week'].id).values(
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    )[0] # unpack dates from current week
    dates = zip(dates.keys(), dates.values()) # zip into tuples

    context = {
        'team': team,
        'form': form,
        'practices': practices,
        'dates': dates,
    }
    context.update(weeks) # include 'weeks' dict in context

    return render(request, 'teams/practice_schedule.html', context)
