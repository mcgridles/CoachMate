from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import teams.tests.test_setup as test
from teams.models import Week

class TeamModelTests(TestCase):
    def setUp(self):
        self.user = test.create_user(username='user', password='password')

    def tearDown(self):
        self.user.delete()

    def test_get_record(self):
        """
        Returns the fastest time for men and women in the given event.
        """
        team = test.create_team(self.user)
        swimmer1 = test.create_swimmer(team)
        swimmer2 = test.create_swimmer(team, first='Jane', last='Doe', gender='F')
        event1 = test.create_event(swimmer1, '50 free', timedelta(seconds=22.32))
        event2 = test.create_event(swimmer1, '50 free', timedelta(seconds=22.96))
        event3 = test.create_event(swimmer2, '50 free', timedelta(seconds=23.51))

        records1 = team.get_record(('50 free', '50 Freestyle'))
        records2 = team.get_record(('100 free', '100 Freestyle'))

        self.assertEqual(records1, ('50 Freestyle', event1, event3))
        self.assertEqual(records2, ('100 Freestyle', None, None))

class SwimmerModelTests(TestCase):
    def setUp(self):
        self.user = test.create_user(username='user', password='password')

    def tearDown(self):
        self.user.delete()

    def test_set_age(self):
        """
        Age function should return current age of swimmer.
        """
        team = test.create_team(self.user)
        swimmer = test.create_swimmer(team, 'Henry', 'Gridley', 'M')
        birth_date = date(1996,9,21)
        age = int((date.today() - birth_date).days / 365.2425)
        self.assertEqual(swimmer.set_age(), age)

    def test_best_time(self):
        """
        Returns the best time in the given event.
        """
        team = test.create_team(user=self.user)
        swimmer = test.create_swimmer(team=team)
        test.create_event(swimmer=swimmer)
        test.create_event(swimmer=swimmer, time=timedelta(seconds=22.96))
        self.assertEqual(swimmer.get_best_time(event='50 free').time, timedelta(seconds=22.32))
        self.assertNotEqual(swimmer.get_best_time(event='50 free').time, timedelta(seconds=22.96))

    def test_get_base(self):
        """
        Returns the base for the given swimmer depending on the pace specified.
        """
        team = test.create_team(self.user)
        swimmer = test.create_swimmer(team)
        base_free = test.create_event(swimmer, 'base free', timedelta(seconds=25))
        race_free = test.create_event(swimmer, '100 free', timedelta(seconds=49.86))

        base_train = swimmer.get_base('train', 'free')
        base_race = swimmer.get_base('race', 'free')
        none_race = swimmer.get_base('race', 'back')
        self.assertEqual(base_train, timedelta(seconds=25))
        self.assertEqual(base_race, timedelta(seconds=24.93))
        self.assertEqual(none_race, None)

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

    def test_date_range(self):
        """
        Yields all dates in a given week.
        """
        week = test.create_week()
        week.populate()
        dates = [
            date(2017,7,10),
            date(2017,7,11),
            date(2017,7,12),
            date(2017,7,13),
            date(2017,7,14),
            date(2017,7,15),
            date(2017,7,16),
        ]
        returned_dates = []
        for day in week.date_range():
            returned_dates.append(day)
        self.assertEqual(dates, returned_dates)
