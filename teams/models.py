# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    birth_date = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True)
    #picture = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.l_name

    def set_age(self):
        """
        Calculate and set age field based on birth date.
        """
        self.age = int((date.today() - self.birth_date).days / 365.2425)
        return self.age

    def get_best_time(self, event):
        """
        Return best time in given event.
        """
        return self.event_set.filter(event=event).order_by('time')[0]


# Events

# Many-to-one -> many times can be created and associated with one swimmer
# Makes it easy to sort and query for fastest time
class Event(models.Model):
    EVENT_CHOICE = (
        ('50 free', '50 Freestyle'),
        ('100 free', '100 Freestyle'),
        ('200 free', '200 Freestyle'),
        ('500 free', '500 Freestyle'),
        ('1000 free', '1000 Freestyle'),
        ('50 back', '50 Backstroke'),
        ('100 back', '100 Backstroke'),
        ('200 back', '200 Backstroke'),
        ('50 breast', '50 Breaststroke'),
        ('100 breast', '100 Breaststroke'),
        ('200 breast', '200 Breaststroke'),
        ('50 fly', '50 Butterfly'),
        ('100 fly', '100 Butterfly'),
        ('200 fly', '200 Butterfly'),
        ('free', 'Freestyle Base'),
        ('back', 'Backstroke Base'),
        ('breaset', 'Breaststroke Base'),
        ('fly', 'Butterfly Base'),
        ('im', 'IM'),
    )

    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    event = models.CharField(max_length=10, choices=EVENT_CHOICE)
    time = models.DurationField()
    date = models.DateField(null=True)

    def __str__(self):
        return self.event


# Could add more classes to organize weeks like a calendar or could do it in views
# Need to figure out how to navigate weeks
class Week(models.Model):
    monday = models.DateField(null=True)
    tuesday = models.DateField(null=True)
    wednesday = models.DateField(null=True)
    thursday = models.DateField(null=True)
    friday = models.DateField(null=True)
    saturday = models.DateField(null=True)
    sunday = models.DateField(null=True)
    present = models.BooleanField()

    def __str__(self):
        return self.monday.isoformat()

    def populate(self):
        """
        Fill in date information for all days based on initial Monday.
        """
        self.tuesday = self.monday + relativedelta(days=1)
        self.wednesday = self.monday + relativedelta(days=2)
        self.thursday = self.monday + relativedelta(days=3)
        self.friday = self.monday + relativedelta(days=4)
        self.saturday = self.monday + relativedelta(days=5)
        self.sunday = self.monday + relativedelta(days=6)
        self.save()

    def get_week(self, n):
        """
        Return previous or next Monday.
        """
        if n is 1:
            monday = self.monday + timedelta(days=7)
        else:
            monday = self.monday - timedelta(days=7)

        return Week.objects.get(monday=monday)


# Training
FOCUS_CHOICE = (
    ('warmup', 'Warmup'),
    ('technique', 'Technique'),
    ('kick', 'Kick'),
    ('sprint', 'Sprint'),
    ('mid-distance', 'Mid Distance'),
    ('distance', 'Distance'),
    ('race', 'Race'),
    ('cooldown', 'Cooldown'),
)
PACE_CHOICE = (
    ('train', 'Base training pace'),
    ('race', '100 race pace'),
)
GROUP_CHOICE = (
    ('team', 'Team'),
    ('ind', 'Individuals'),
)

# Sets day, week, and team for each group of sets
class Practice(models.Model):
    DAY_CHOICE = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    week_id = models.ForeignKey(Week, on_delete=models.CASCADE, null=True)
    weekday = models.CharField(max_length=10, choices=DAY_CHOICE)

    def __str__(self):
        return self.weekday

# Overall focus and repeats
class Set(models.Model):
    practice_id = models.ForeignKey(Practice, on_delete=models.CASCADE)
    group = models.CharField(max_length=25, choices=GROUP_CHOICE, null=True)
    swimmers = models.ManyToManyField(Swimmer, blank=True)
    focus = models.CharField(max_length=15, choices=FOCUS_CHOICE)
    repeats = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(null=True) # creates order within a practice
    pace = models.CharField(max_length=10, choices=PACE_CHOICE, null=True)

    def __str__(self):
        return self.focus

# Individual items in a set
class Rep(models.Model):
    STROKE_CHOICE = (
        ('fly', 'Butterfly'),
        ('back', 'Backstroke'),
        ('breast', 'Breaststroke'),
        ('free', 'Freestyle'),
        ('im', 'IM'),
    )

    set_id = models.ForeignKey(Set, on_delete=models.CASCADE)
    num = models.IntegerField()
    distance = models.IntegerField()
    stroke = models.CharField(max_length=6, choices=STROKE_CHOICE)
    rest = models.DurationField(blank=True, null=True)
    comments = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return self.stroke

class Interval(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    rep = models.ForeignKey(Rep, on_delete=models.CASCADE)
    time = models.DurationField()

# Guide for doing interval calculations
class TrainingModel(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.team.abbr

class TrainingMultiplier(models.Model):
    training_model = models.ForeignKey(TrainingModel, on_delete=models.CASCADE)
    focus = models.CharField(max_length=15, choices=FOCUS_CHOICE)
    multiplier = models.FloatField(null=True)

    def __str__(self):
        return self.focus
