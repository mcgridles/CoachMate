# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from teams.models import Team, Swimmer, Event, Set, Rep, Practice, Week

def create_user(username, password):
    """
    Create a test user.
    """
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user

def create_team(user, name='Northeastern University', abbr='NUSC', region='ECC'):
    """
    Create a test team.
    """
    return Team.objects.create(
        user=user,
        name=name,
        abbr=abbr,
        region=region
    )

def create_swimmer(team, first='Henry', last='Gridley', gender='M'):
    """
    Create a test swimmer with the given name.
    """
    return Swimmer.objects.create(
        team=team,
        f_name=first,
        l_name=last,
        gender=gender,
        birth_date=date(1996, 9, 21),
        bio='',
    )

def create_event(swimmer, event='50 free', time=timedelta(seconds=22, milliseconds=320)):
    """
    Create a test event.
    """
    return Event.objects.create(
        swimmer=swimmer,
        event=event,
        time=time,
    )

def create_week(monday=date(2017,7,10), present=False):
    """
    Create a test week.
    """
    return Week.objects.create(monday=monday, present=present)

def create_practice(team, week, weekday='monday'):
    """
    Create a test practice.
    """
    return Practice.objects.create(
        team=team,
        week_id=week,
        weekday=weekday,
    )

def create_set(practice, focus='warmup', repeats=1, order=1):
    """
    Create a test set.
    """
    return Set.objects.create(
        practice_id=practice,
        focus=focus,
        repeats=repeats,
        order=order,
    )

def create_rep(_set, num=10, distance=100, stroke='free'):
    """
    Create a test rep.
    """
    return Rep.objects.create(
        set_id=_set,
        num=num,
        distance=distance,
        stroke=stroke,
    )
