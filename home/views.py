# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

# Homepage

def home(request):
    if request.user.is_authenticated():
        return redirect('teams:teamList')
    else:
        if DEBUG:
            return render(request, 'home/homepage.html', {})
        else:
            return render(request, 'home/homepage.min.html', {})
