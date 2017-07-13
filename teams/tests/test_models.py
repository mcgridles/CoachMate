from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import teams.tests.test_setup as test

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

    def test_check_current(self):
        """
        If the current week is found, the current boolean value will be set to
        True and the boolean value of the previous week will be set to False.
        """
        current_week = test.create_week()
        previous_week = test.create_week(date(2017,7,3), True)
        current_week.populate()
        current_week.check_current()
        previous_week.refresh_from_db()
        self.assertEqual(current_week.current, True)
        self.assertEqual(previous_week.current, False)
