# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from accounts.forms import SignUpForm, LogInForm, SettingsForm

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
                return redirect('teams:teamList')
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
            return redirect('teams:teamList')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@csrf_protect
@login_required
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            #requires old password + new password and confirmation to change
            old_passwd = form.cleaned_data['old_passwd']
            new_passwd1 = form.cleaned_data['new_passwd1']
            new_passwd2 = form.cleaned_data['new_passwd2']

            user = auth.authenticate(username=request.user.username, password=old_passwd)
            if user is not None:
                if new_passwd1 == new_passwd2:
                    user.set_password(new_passwd1)
                    user.save()
                    auth.login(request, user) # log in user for redirect
                    messages.success(request, 'Password changed')
                else:
                    messages.error(request, 'Passwords do not match')
            else:
                messages.error(request, 'Incorrect password')
        else:
            messages.error(request, 'Invalid entry')

        return redirect('accounts:settings')

    else:
        form = SettingsForm()
    return render(request, 'accounts/settings.html', {'form': form, 'user': request.user})
