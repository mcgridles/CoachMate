# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-03 20:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='swimmer',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Fale')], max_length=1),
        ),
    ]
