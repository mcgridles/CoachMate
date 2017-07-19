# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-10 00:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0009_auto_20170708_2057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rep',
            name='rest',
        ),
        migrations.RemoveField(
            model_name='week',
            name='end',
        ),
        migrations.AddField(
            model_name='practice',
            name='week_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teams.Week'),
        ),
        migrations.AddField(
            model_name='week',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]