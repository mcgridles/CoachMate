# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Not sure how to associate things with a user but we may need to give the
# Team and Week classes a ForeignKey field for a user


# Swimmers & Teams

class Team(models.Model):
    name = models.CharField(max_length=50)
    num_swimmers = models.IntegerField()
    region = models.CharField(max_length=25)

class Swimmer(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    f_name = models.CharField(max_length=25)
    l_name = models.CharField(max_length=25)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    bio = models.TextField()

# Calendar

# Need to be able to associate practice with a day of the week
# Could add more class to organize weeks like a calendar or could do it in views
class Week(models.Model):
    # start and end can be used to keep track of dates
    start = models.DateField()
    end = models.DateField()

# Workout

class Practice(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    weekday = models.CharField(max_length=10)
    description = models.TextField()

class Set(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    repeats = models.IntegerField()

class Rep(models.Model):
    set_id = models.ForeignKey(Set, on_delete=models.CASCADE)

    num = models.IntegerField()
    distance = models.IntegerField()
    stroke = models.CharField(max_length=10)
    comments = models.CharField(max_length=100) # switch to TextField?

# Events

# Many-to-one -> many times can be created and associated with one swimmer
# Makes it easy to sort and query for fastest time
class Free_50(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Free_100(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Free_200(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Free_500(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Free_1000(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Fly_50(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Fly_100(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Fly_200(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Back_50(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Back_100(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Back_200(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Breast_50(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Breast_100(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()

class Breast_200(models.Model):
    swimmer = models.ForeignKey(Swimmer, on_delete=models.CASCADE)
    time = models.DurationField()
