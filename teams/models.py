# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date, timedelta
#from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.l_name

    def get_age(self):
        return int((date.today() - self.birth_date).days / 365.2425)

    def get_best_time(self, event):
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
    )

    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    event = models.CharField(max_length=10, choices=EVENT_CHOICE)
    time = models.DurationField()

    def __str__(self):
        return self.event


# Calendar

# Need to be able to associate practice with a day of the week
# Could add more class to organize weeks like a calendar or could do it in views
class Week(models.Model):
    monday = models.DateField(null=True)
    tuesday = models.DateField(null=True)
    wednesday = models.DateField(null=True)
    thursday = models.DateField(null=True)
    friday = models.DateField(null=True)
    saturday = models.DateField(null=True)
    sunday = models.DateField(null=True)
    current = models.BooleanField()

    def __str__(self):
        return self.monday.isoformat()

    def populate(self):
        # use relativedelta
        self.tuesday = self.monday + timedelta(days=1)
        self.wednesday = self.monday + timedelta(days=2)
        self.thursday = self.monday + timedelta(days=3)
        self.friday = self.monday + timedelta(days=4)
        self.saturday = self.monday + timedelta(days=5)
        self.sunday = self.monday + timedelta(days=6)

    def date_range(self):
        for n in range(int((self.sunday - self.monday).days)):
            yield self.monday + timedelta(n)

    # make standalone function
    def check_current(self):
        for date in self.date_range():
            if date == date.today():
                previous_week = Week.objects.exclude(monday=self.monday).update(current=False)

                self.current = True
                self.save()
                return self.current

        self.current = False
        self.save()
        return self.current

    def get_prev_week(self):
        return Week.objects.filter(monday__lt=self.monday).order_by('-monday')[0]

    def get_next_week(self):
        return Week.objects.filter(monday__gt=self.monday).order_by('monday')[0]


# Workout

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

class Set(models.Model):
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

    practice_id = models.ForeignKey(Practice, on_delete=models.CASCADE)
    focus = models.CharField(max_length=15, choices=FOCUS_CHOICE, blank=True)
    repeats = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(null=True)

    def __str__(self):
        return self.focus

class Rep(models.Model):
    STROKE_CHOICE = (
        ('fly', 'Butterfly'),
        ('back', 'Backstroke'),
        ('breast', 'Breaststroke'),
        ('free', 'Freestyle'),
        ('im', 'IM'),
        ('kick', 'Kick'),
    )

    set_id = models.ForeignKey(Set, on_delete=models.CASCADE)
    num = models.IntegerField()
    distance = models.IntegerField()
    stroke = models.CharField(max_length=6, choices=STROKE_CHOICE)
    rest = models.DurationField(blank=True, null=True)
    comments = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return self.stroke
