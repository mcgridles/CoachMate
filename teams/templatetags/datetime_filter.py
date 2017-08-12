from django import template

from datetime import date, timedelta

register = template.Library()

@register.filter(name='format_duration')
def format_duration(value):
    """
    Format duration fields to be m:ss.
    """
    hours, rem = divmod(value.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return '{:02d}:{:02d}'.format(minutes, seconds)

@register.filter(name='format_record')
def format_record(value):
    """
    Format duration fields to be MM:ss.mm
    """
    min, sec = divmod(value.total_seconds(), 60)
    min = int(min)
    return '{:02d}:{:05.2f}'.format(min, sec)
