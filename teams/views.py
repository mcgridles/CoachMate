# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

from teams.models import *
from teams.forms import *
import teams.functions as funct
from teams.TeamManager import TeamManager
from teams.graphs import graph_event
from CoachMate.settings.base import DEBUG

logger = logging.getLogger('CoachMate.prod') # Logger for production logging if necessary
logger_debug = logging.getLogger('CoachMate.dev') # Logger for debugging

@csrf_protect
@login_required
def teamList(request):
    if request.method == 'POST':
        team_form = TeamForm(request.POST, user=request.user)
        if team_form.is_valid():
            try:
                # do nothing if team already exists
                team_name = team_form.cleaned_data['name']
                team = Team.objects.filter(user=request.user).get(name=team_name)
            except:
                # else create new team
                team_form.save()
                return redirect('teams:teamList')
    else:
        team_form = TeamForm()

    team_list = Team.objects.filter(user=request.user)
    context = {
        'team_form': team_form,
        'team_list': team_list,
    }

    if DEBUG:
        return render(request, 'teams/team_list.html', context)
    else:
        return render(request, 'teams/team_list.min.html', context)


# Delete a team
@login_required
def deleteTeam(request, abbr):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    team.delete()
    return redirect('teams:teamList')


# Team records
@login_required
def teamRecords(request, abbr):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    records = funct.get_team_records(team)

    if request.method == 'POST':
        record_form = RecordForm(request.POST, team=team)
        if record_form.is_valid():
            record = record_form.save()
            return redirect('teams:teamRecords', abbr=team.abbr)

    else:
        record_form = RecordForm(team=team)

    context = {
        'team': team,
        'records': records,
        'record_form': record_form,
    }

    if DEBUG:
        return render(request, 'teams/team_records.html', context)
    else:
        return render(request, 'teams/team_records.min.html', context)


@csrf_protect
@login_required
def swimmerList(request, abbr):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    if request.method == 'POST':
        if 'swimmer_create' in request.POST:
            swimmer_form = SwimmerForm(request.POST, team=team)
            if swimmer_form.is_valid():
                last_name = swimmer_form.cleaned_data['l_name']
                first_name = swimmer_form.cleaned_data['f_name']
                try:
                    # do nothing if swimmer already exists
                    swimmer = Swimmer.objects.filter(team=team).filter(
                        l_name=last_name).get(f_name=first_name)
                except:
                    # else create new swimmer
                    new_swimmer = swimmer_form.save()
                    return redirect('teams:swimmerList', abbr=team.abbr)
            else:
                team_form = TeamForm(instance=team)
                upload_form = UploadZipForm()

        elif 'team_edit' in request.POST:
            team_form = TeamForm(request.POST, instance=team, user=request.user)
            if team_form.is_valid():
                team_form.save()
                return redirect('teams:swimmerList', abbr=team.abbr)
            else:
                swimmer_form = SwimmerForm()
                upload_form = UploadZipForm()

        # upload team rosters and meet results
        elif 'upload' in request.POST:
            upload_form = UploadZipForm(request.POST, request.FILES)
            if upload_form.is_valid():
                zip_file = request.FILES['zip_file']
                tm = TeamManager(team=team, zip_file=zip_file) # team manager object
                # msgs contains error or success messages
                if 'Roster' in zip_file.name:
                    msgs = tm.load_roster()
                elif 'Results' in zip_file.name:
                    msgs = tm.load_results()
                else:
                    msgs = ('error', 'Invalid file')

                for message in msgs:
                    if message[0] == 'success':
                        messages.success(request, message[1])
                    else:
                        messages.error(request, message[1])
                return redirect('teams:swimmerList', abbr=team.abbr)
            else:
                team_form = TeamForm(instance=team)
                swimmer_form = SwimmerForm()
    else:
        swimmer_form = SwimmerForm()
        team_form = TeamForm(instance=team)
        upload_form = UploadZipForm()

    swimmer_list  = Swimmer.objects.filter(team=team)
    context = {
        'team': team,
        'team_form': team_form,
        'swimmer_list': swimmer_list,
        'swimmer_form': swimmer_form,
        'upload_form': upload_form,
    }

    if DEBUG:
        return render(request, 'teams/swimmer_list.html', context)
    else:
        return render(request, 'teams/swimmer_list.min.html', context)


# Individual swimmer pages
@csrf_protect
@login_required
def swimmerDetail(request, abbr, s_id):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    swimmer = get_object_or_404(Swimmer, pk=s_id)

    if request.method == 'POST':
        if 'edit_swimmer' in request.POST:
            swimmer_form = SwimmerForm(request.POST, request.FILES, instance=swimmer, team=team)
            if swimmer_form.is_valid():
                swimmer_form.save()
                event_form = EventForm(swimmer=swimmer)
                return redirect('teams:swimmerDetail', abbr=team.abbr, s_id=swimmer.id)
            else:
                event_form = EventForm(swimmer=swimmer)

        elif 'add_event' in request.POST:
            event_form = EventForm(request.POST, swimmer=swimmer)
            if event_form.is_valid():
                event = event_form.save()
                swimmer_form = SwimmerForm(instance=swimmer)
                return redirect('teams:swimmerDetail', abbr=team.abbr, s_id=swimmer.id)
            else:
                swimmer_form = SwimmerForm(instance=swimmer)
        else:
            swimmer_form = SwimmerForm(instance=swimmer)
            event_form = EventForm(swimmer=swimmer)

    else:
        swimmer_form = SwimmerForm(instance=swimmer)
        event_form = EventForm(swimmer=swimmer)

    script, div = graph_event(swimmer)
    records = funct.get_swimmer_records(swimmer)

    context =  {
        'team': team,
        'swimmer': swimmer,
        'swimmer_form': swimmer_form,
        'event_form': event_form,
        'script': script,
        'div': div,
        'records': records,
    }

    if DEBUG:
        return render(request, 'teams/swimmer_detail.html', context)
    else:
        return render(request, 'teams/swimmer_detail.min.html', context)


# Delete a swimmer
@login_required
def deleteSwimmer(request, abbr, s_id):
    swimmer = get_object_or_404(Swimmer, pk=s_id)
    swimmer.delete()
    return redirect('teams:swimmerList', abbr=abbr)


@csrf_protect
@login_required
def writePractice(request, abbr, p_id):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    practice = get_object_or_404(Practice, Q(team=team), pk=p_id)
    week = get_object_or_404(Week, pk=practice.week_id.id)
    try:
        training_model = TrainingModel.objects.get(team=team)
    except TrainingModel.DoesNotExist:
        training_model = None

    if request.method == 'POST':
        if 'set_create' in request.POST:
            set_form = SetForm(data=request.POST, practice=practice, team=team)
            rep_formset = RepFormSet(request.POST)
            if set_form.is_valid() and rep_formset.is_valid():
                # checking now instead of when the practice is created means the
                # previous practice is not lost until this one is populated with sets
                funct.clean_weekday(team, practice)

                # get set form instance
                setInstance = set_form.save()
                rest_flag = rep_formset.save_formset(setInstance) # set set_id for each rep

                if rest_flag == False:
                    i = funct.calculate_intervals(setInstance, training_model)
                    if i == False:
                        messages.error(request, 'No training model - Couldn\'t calculate intervals')

                return redirect('teams:writePractice', abbr=team.abbr, p_id=p_id)

            else:
                practice_form = PracticeForm(instance=practice)

        elif 'practice_edit' in request.POST:
            practice_form = PracticeForm(request.POST, instance=practice, team=team, week=week)
            if practice_form.is_valid():
                practice_form.save()
                return redirect('teams:writePractice', abbr=team.abbr, p_id=p_id)
            else:
                set_form = SetForm(team=team)
                rep_formset = RepFormSet()

    else:
        set_form = SetForm(team=team)
        rep_formset = RepFormSet()
        practice_form = PracticeForm(instance=practice)

    set_list = Set.objects.filter(practice_id=p_id)
    context = {
        'team': team,
        'practice': practice,
        'week': practice.week_id.id,
        'set_list': set_list,
        'set_form': set_form,
        'rep_formset': rep_formset,
        'practice_form': practice_form,
    }

    if DEBUG:
        return render(request, 'teams/practice_write.html', context)
    else:
        return render(request, 'teams/practice_write.min.html', context)



# Delete a set
@login_required
def deleteSet(request, abbr, set_id):
    _set = get_object_or_404(Set, pk=set_id)
    w_id = get_object_or_404(Week, pk=_set.practice_id.week_id.id).id
    _set.delete()
    return redirect('teams:practiceSchedule', abbr=abbr, w_id=w_id)


# Delete a practice
@login_required
def deletePractice(request, abbr, p_id):
    practice = get_object_or_404(Practice, pk=p_id)
    w_id = practice.week_id.id
    practice.delete()
    return redirect('teams:practiceSchedule', abbr=abbr, w_id=w_id)


@csrf_protect
@login_required
def practiceSchedule(request, abbr, w_id):
    team = get_object_or_404(Team, Q(user=request.user), abbr=abbr)
    weeks = funct.get_or_create_weeks(w_id)

    if request.method == 'POST':
        practice_form = PracticeForm(request.POST, team=team, week=weeks['current'])
        if practice_form.is_valid():
            # create new practice with no sets
            # allows new sets to be associated with a practice
            practice = practice_form.save()

            # don't need?
            context = {
                'team': team,
                'practice': practice,
            }
            return redirect('teams:writePractice', abbr=team.abbr, p_id=practice.id)
    else:
        practice_form = PracticeForm()

    practices, dates = funct.get_practices_and_dates(team, weeks)

    context = {
        'team': team,
        'practice_form': practice_form,
        'practices': practices,
        'dates': dates,
    }
    context.update(weeks) # include 'weeks' dict in context

    if DEBUG:
        return render(request, 'teams/practice_schedule.html', context)
    else:
        return render(request, 'teams/practice_schedule.min.html', context)


@csrf_protect
@login_required
def createTraining(request, t_id):
    if int(t_id) is 0:
        training_model = None
        multiplier_set = TrainingMultiplier.objects.none()
    else:
        training_model = get_object_or_404(TrainingModel, pk=t_id)
        multiplier_set = TrainingMultiplier.objects.filter(training_model=training_model)

    if request.method == 'POST':
        training_form = TrainingForm(request.POST, instance=training_model)
        multiplier_formset = MultiplierFormSet(request.POST, queryset=multiplier_set)
        if training_form.is_valid() and multiplier_formset.is_valid():
            trainingInstance = training_form.save()
            multiplier_formset.save(trainingInstance)
            return redirect('teams:showTraining')

    else:
        training_form = TrainingForm(instance=training_model)
        multiplier_formset = MultiplierFormSet(queryset=multiplier_set)

    context = {
        't_id': t_id,
        'training_form': training_form,
        'multiplier_formset': multiplier_formset,
    }

    if DEBUG:
        return render(request, 'teams/training_create.html', context)
    else:
        return render(request, 'teams/training_create.min.html', context)


@login_required
def deleteTraining(request, t_id):
    training_model = get_object_or_404(TrainingModel, pk=t_id)
    training_model.delete()
    return redirect('teams:showTraining')


@csrf_protect
@login_required
def showTraining(request):
    teams = Team.objects.filter(user=request.user)

    models = []
    for team in teams:
        try:
            training_model = TrainingModel.objects.get(team=team)
        except TrainingModel.DoesNotExist:
            training_model = None
        models.append(training_model)

    teams = zip(teams, models)

    context = {
        'teams': teams,
    }

    if DEBUG:
        return render(request, 'teams/training_show.html', context)
    else:
        return render(request, 'teams/training_show.min.html', context)
