# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-30 06:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0026_auto_20170730_0200'),
    ]

    operations = [
        migrations.AddField(
            model_name='set',
            name='group',
            field=models.CharField(choices=[('team', 'Team'), ('ind', 'Individuals')], max_length=25, null=True),
        ),
    ]