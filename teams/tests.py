# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from teams.models import Team, Swimmer

def create_user():
    """
    Creates a test user
    """
    return User.objects.create_user('John', 'johndoe@example.com', 'johndoepassword')

def create_team():
    """
    Creates a test team
    """
    user = create_user()
    return Team.objects.create(
        user=user,
        name='Northeastern University Swim Club',
        abbr='NUSC',
        region='ECC'
    )

def create_swimmer(first, last, gender):
    """
    Creates a test swimmer with the given name
    """
    team = create_team()
    return Swimmer.objects.create(
        team=team,
        f_name=first,
        l_name=last,
        gender=gender,
        age=20,
        bio=''
    )
