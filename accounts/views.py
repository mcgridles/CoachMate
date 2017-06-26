# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

def login(request):
    name = 'CoachMate'
    context = {'name': name}
    return render(request, 'accounts/login.html', context)

def signup(request):
    name = 'CoachMate'
    context = {'name': name}
    return render(request, 'accounts/signup.html', context)
