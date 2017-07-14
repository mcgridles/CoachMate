# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect

from accounts.forms import SignUpForm, LogInForm

@csrf_protect
def login(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # authenticate user
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user) # log in user
                return redirect('teams:team_list')
            else:
                form = LogInForm()
                return render(request, 'accounts/login.html', {'form': form})
    else:
        form = LogInForm()
        return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    auth.logout(request)
    return redirect('home')

@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # authenticate user
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user) # log in user
            return redirect('teams:team_list')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
