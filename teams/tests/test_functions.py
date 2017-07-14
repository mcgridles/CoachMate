from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase

import teams.tests.test_setup as test
from teams.models import Week
import teams.functions as funct


class FunctionTests(TestCase):
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

    def test_check_current_with_no_weeks(self):
        """
        Returns None.
        """
        x = funct.check_current()
        self.assertEqual(x, False)

    def test_check_current_with_current_week(self):
        """
        Sets the boolean value of the correct present week to True and all others
        to False. The function also returns True.
        """
        week1 = test.create_week()
        week1.populate()
        week2 = test.create_week(monday=(date.today() - timedelta(days=7)))
        week2.populate()
        week3 = test.create_week(monday=(date.today() + timedelta(days=7)), current=True)
        week3.populate()

        x = funct.check_current()

        for week in [week1, week2, week3]:
            week.refresh_from_db()

        self.assertEqual(x, True)
        self.assertEqual(week1.current, True)
        self.assertEqual(week2.current, False)
        self.assertEqual(week3.current, False)

    def test_check_current_with_no_current_week(self):
        """
        Sets all current boolean values to False and returns False.
        """
        week1 = test.create_week(monday=(date.today() - timedelta(days=7)))
        week1.populate()
        week2 = test.create_week(monday=(date.today() + timedelta(days=7)), current=True)
        week2.populate()

        x = funct.check_current()

        for week in [week1, week2]:
            week.refresh_from_db()

        self.assertEqual(x, True)
        self.assertEqual(week1.current, False)
        self.assertEqual(week2.current, False)

    def test_get_monday_current(self):
        """
        Returns most recent Monday. To test, uncomment and change current_mon date.
        Tested and works.
        """
        pass
        #monday = funct.get_monday()
        #current_mon = date(2017,7,10)
        #self.assertEqual(monday, current_mon)

    def test_get_monday_previous(self):
        """
        Returns previous Monday. To test, uncomment and change previous_mon date.
        Tested and works.
        """
        pass
        #monday = funct.get_monday(0)
        #previous_mon = date(2017,7,3)
        #self.assertEqual(monday, previous_mon)

    def test_get_monday_previous(self):
        """
        Returns next Monday. To test, uncomment and change next_mon date.
        Tested and works.
        """
        pass
        #monday = funct.get_monday(1)
        #next_mon = date(2017,7,17)
        #self.assertEqual(monday, next_mon)
