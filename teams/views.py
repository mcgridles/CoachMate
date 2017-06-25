# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
def teams(request):
    name = 'CoachMate'
    context = {'name': name}
    return render(request, 'teams/base.html', context)
