from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import teams.tests.test_setup as test
from teams.models import Week

class SwimmerModelTests(TestCase):
    def setUp(self):
        self.user = test.create_user(username='user', password='password')

    def tearDown(self):
        self.user.delete()

    def test_age(self):
        """
        Age function should return current age of swimmer.
        """
        team = test.create_team(self.user)
        swimmer = test.create_swimmer(team, 'Henry', 'Gridley', 'M')
        birth_date = date(1996,9,21)
        age = int((date.today() - birth_date).days / 365.2425)
        self.assertEqual(swimmer.get_age(), age)

    def test_best_time(self):
        """
        The best time in the given event should be returned.
        """
        team = test.create_team(user=self.user)
        swimmer = test.create_swimmer(team=team)
        test.create_event(swimmer=swimmer)
        test.create_event(swimmer=swimmer, time=timedelta(seconds=22, milliseconds=960))
        self.assertEqual(swimmer.get_best_time(event='50 free').time, timedelta(seconds=22, milliseconds=320))
        self.assertNotEqual(swimmer.get_best_time(event='50 free').time, timedelta(seconds=22, milliseconds=960))

class WeekModelTests(TestCase):
    def test_populate(self):
        """
        When given the date for a Monday, the Week object will populate the dates
        for every day of the week.
        """
        week = test.create_week()
        week.populate()
        tuesday = date(2017,7,11)
        sunday = date(2017,7,16)
        self.assertEqual(week.tuesday, tuesday)
        self.assertEqual(week.sunday, sunday)

    def test_get_week_with_no_weeks(self):
        """
        Raises a DoesNotExist error if either week has not been created.
        """
        week = test.create_week()
        self.assertRaises(Week.DoesNotExist, week.get_week, n=1)

    def test_get_week_with_weeks(self):
        """
        Returns the corresponding week, either next or previous.
        """
        week = test.create_week()
        previous = test.create_week(monday=date(2017,7,3))
        self.assertEqual(week.get_week(-1), previous)
