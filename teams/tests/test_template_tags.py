from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase

from teams.templatetags.datetime_filter import format_duration

class TestFormatDuration(TestCase):
    def test_format_duration_with_no_time(self):
        """
        AttributeError is raised if format_duration is not passed a timedelta.
        """
        self.assertRaises(AttributeError, format_duration, None)

    def test_format_duration_with_time(self):
        """
        Returns the timedelta formatted as mm:ss.
        """
        time1 = timedelta(minutes=1, seconds=20)
        time2 = timedelta(minutes=0, seconds=5)
        time3 = timedelta(minutes=70, seconds=0)
        time4 = timedelta(minutes=100, seconds=61)
        self.assertEqual(format_duration(time1), '01:20')
        self.assertEqual(format_duration(time2), '00:05')
        self.assertEqual(format_duration(time3), '10:00')
        self.assertEqual(format_duration(time4), '41:01')
