# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

# Not sure how to associate things with a user but we may need to give the
# Team and Week classes a ForeignKey field for a user


# Swimmers & Teams

class Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=5)
    region = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.name

class Swimmer(models.Model):
    GENDER_CHOICE = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    f_name = models.CharField(max_length=25)
    l_name = models.CharField(max_length=25)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    age = models.IntegerField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.l_name


# Calendar

# Need to be able to associate practice with a day of the week
# Could add more class to organize weeks like a calendar or could do it in views
class Week(models.Model):
    # start and end can be used to keep track of dates
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return self.start


# Workout

class Practice(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    weekday = models.CharField(max_length=10)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.weekday

class Set(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    repeats = models.IntegerField(blank=True)

class Rep(models.Model):
    STROKE_CHOICE = (
        ('fly', 'Butterfly'),
        ('back', 'Backstroke'),
        ('breast', 'Breaststroke'),
        ('free', 'Freestyle'),
    )

    set_id = models.ForeignKey(Set, on_delete=models.CASCADE)
    num = models.IntegerField()
    distance = models.IntegerField()
    stroke = models.CharField(max_length=6, choices = STROKE_CHOICE)
    comments = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.stroke


# Events

# Many-to-one -> many times can be created and associated with one swimmer
# Makes it easy to sort and query for fastest time
class Event(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    event = models.CharField(max_length=20)
    time = models.DurationField()

    def __str__(self):
        return self.event


# Model forms

class TeamForm(ModelForm):
    class Meta:
        model = Team
        exclude = ['user']
        labels = {
            'name': 'Team Name',
            'abbr': 'Team Abbreviation',
            'region': 'Team Region',
        }

class SwimmerForm(ModelForm):
    class Meta:
        model = Swimmer
        exclude = ['team']
        labels = {
            'f_name': 'First Name',
            'l_name': 'Last Name',
            'gender': 'M/F',
            'age': 'Age',
            'bio': 'Bio',
        }
