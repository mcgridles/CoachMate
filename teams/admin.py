# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from teams.models import Team, Swimmer

class SwimmerInline(admin.StackedInline):
    model = Swimmer
    extra = 2

class TeamAdmin(admin.ModelAdmin):
    fields = ('name', 'abbr', 'region')
    inlines = [SwimmerInline]
    list_display = ('name', 'region')
    search_fields = ['name', 'region']

admin.site.register(Team, TeamAdmin)
