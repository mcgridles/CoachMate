# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

def home(request):
    name = 'CoachMate'
    context = {'name': name}
    return render(request, 'home/homepage.html', context)
