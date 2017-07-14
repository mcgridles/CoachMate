from django import template

from datetime import date, timedelta

register = template.Library()

@register.filter(name='format_duration')
def format_duration(value):
    hours, rem = divmod(value.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return '{:02d}:{:02d}'.format(minutes, seconds)
