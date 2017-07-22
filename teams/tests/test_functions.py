from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date
from dateutil.relativedelta import relativedelta

from django.test import TestCase

import teams.tests.test_setup as test
from teams.models import Week, Practice
import teams.functions as funct


class FunctionTests(TestCase):
    def setUp(self):
        self.user = test.create_user('user', 'password')

    def tearDown(self):
        self.user.delete()

    def test_get_monday_present(self):
        """
        Returns most recent Monday. To test, uncomment and change current_mon date.
        Tested and works.
        """
        week = test.create_week()
        week.populate()
        monday = funct.get_monday(week=week)
        current_mon = date(2017,7,10)
        self.assertEqual(monday, current_mon)

    def test_get_monday_previous(self):
        """
        Returns previous Monday. To test, uncomment and change previous_mon date.
        Tested and works.
        """
        week = test.create_week()
        week.populate()
        monday = funct.get_monday(week, 0)
        previous_mon = date(2017,7,3)
        self.assertEqual(monday, previous_mon)

    def test_get_monday_next(self):
        """
        Returns next Monday. To test, uncomment and change next_mon date.
        Tested and works.
        """
        week = test.create_week()
        week.populate()
        monday = funct.get_monday(week, 1)
        next_mon = date(2017,7,17)
        self.assertEqual(monday, next_mon)

    def test_date_range(self):
        """
        Yields all dates in a given week.
        """
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
        for day in funct.date_range(date(2017,7,10), date(2017,7,16)):
            returned_dates.append(day)
        self.assertEqual(dates, returned_dates)

    def test_check_present_with_no_weeks(self):
        """
        Returns None.
        """
        out = funct.check_present()
        self.assertFalse(out)

    def test_check_present_with_present_week(self):
        """
        Sets the boolean value of the correct present week to True and all others
        to False. The function also returns True.
        """
        mon_present = funct.get_monday(n=None)
        mon_previous = funct.get_monday(n=0)
        mon_next = funct.get_monday(n=1)
        week1 = test.create_week(monday=mon_present)
        week1.populate()
        week2 = test.create_week(monday=mon_previous)
        week2.populate()
        week3 = test.create_week(monday=mon_next, present=True)
        week3.populate()

        out = funct.check_present()

        for week in [week1, week2, week3]:
            week.refresh_from_db()

        self.assertTrue(out)
        self.assertTrue(week1.present)
        self.assertFalse(week2.present)
        self.assertFalse(week3.present)

    def test_check_present_with_no_present_week(self):
        """
        Sets all current boolean values to False and returns False.
        """
        week1 = test.create_week(monday=(date.today() - relativedelta(days=7)))
        week1.populate()
        week2 = test.create_week(monday=(date.today() + relativedelta(days=7)), present=True)
        week2.populate()

        out = funct.check_present()

        for week in [week1, week2]:
            week.refresh_from_db()

        self.assertTrue(out)
        self.assertFalse(week1.present)
        self.assertFalse(week2.present)

    def test_clean_weekday(self):
        """
        Only one practice can exist on a weekday for each given week.
        """
        week1 = test.create_week(monday=date.today())
        week1.populate()
        week2 = test.create_week(monday=(date.today() + relativedelta(days=7)))
        week2.populate()
        team = test.create_team(user=self.user)
        practice1 = test.create_practice(team, week1)
        practice2 = test.create_practice(team, week1)
        practice3 = test.create_practice(team, week2)

        funct.clean_weekday(team, practice2)

        practices = Practice.objects.all()
        self.assertQuerysetEqual(
            practices,
            ['<Practice: monday>', '<Practice: monday>'],
            ordered=False
        )
        self.assertTrue(practice1 not in practices)

    def test_get_or_create_weeks_with_no_weeks(self):
        """
        The previous, current, and next weeks should be created and added to a dict.
        """
        weeks = funct.get_or_create_weeks(0)
        self.assertEqual(sorted(weeks.keys()), ['current', 'next', 'previous'])
        self.assertEqual(weeks['current'].monday, funct.get_monday())
        self.assertEqual(weeks['previous'].monday, funct.get_monday(None, 0))
        self.assertEqual(weeks['next'].monday, funct.get_monday(None, 1))

    def test_get_or_create_weeks_with_weeks(self):
        """
        The previous, current, and next weeks should be added to a dict.
        """
        previous_week = test.create_week(monday=funct.get_monday(None, 0))
        previous_week.populate()
        current_week = test.create_week(monday=funct.get_monday())
        current_week.populate()
        next_week = test.create_week(monday=funct.get_monday(None, 1))
        next_week.populate()
        weeks = funct.get_or_create_weeks(0)
        self.assertEqual(sorted(weeks.keys()), ['current', 'next', 'previous'])
        self.assertEqual(weeks['current'].monday, current_week.monday)
        self.assertEqual(weeks['previous'].monday, previous_week.monday)
        self.assertEqual(weeks['next'].monday, next_week.monday)

    def test_get_practices_and_dates(self):
        self.maxDiff = None
        """
        Returns a list of practices and a list of dates.
        """
        weeks = funct.get_or_create_weeks(0)
        team = test.create_team(user=self.user)
        practices, dates = funct.get_practices_and_dates(team, weeks)

        test_dates = []
        for day in funct.date_range(weeks['current'].monday, weeks['current'].sunday):
            test_dates.append(day)

        self.assertEqual(practices, [
            (None, 'monday'),
            (None, 'tuesday'),
            (None, 'wednesday'),
            (None, 'thursday'),
            (None, 'friday'),
            (None, 'saturday'),
            (None, 'sunday'),
        ])
        self.assertEqual(dates, [
            ('monday', test_dates[0]),
            ('tuesday', test_dates[1]),
            ('friday', test_dates[4]),
            ('wednesday', test_dates[2]),
            ('thursday', test_dates[3]),
            ('sunday', test_dates[6]),
            ('saturday', test_dates[5]),
        ])
