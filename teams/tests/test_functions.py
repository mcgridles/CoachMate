from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase

import teams.tests.test_setup as test
from teams.models import Week, Practice, Interval
import teams.functions as funct


class TestFunctions(TestCase):
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
        """
        Returns a list of practices and a list of dates.
        """
        weeks = funct.get_or_create_weeks(0)
        team = test.create_team(user=self.user)
        swimmer1 = test.create_swimmer(team)
        base_free = test.create_event(swimmer1, event='base free', time=timedelta(seconds=25))
        swimmer2 = test.create_swimmer(team, first='Dave', last='Thornton')
        practice = test.create_practice(team, weeks['current'])
        setInstance = test.create_set(practice=practice, swimmers=[swimmer1, swimmer2])
        rep1 = test.create_rep(setInstance)

        training_model = test.create_training_model(team)
        training_mult = test.create_training_multiplier(training_model, multiplier=0.07)
        funct.calculate_intervals(setInstance, training_model)

        practices, dates = funct.get_practices_and_dates(team, weeks)

        test_dates = []
        for day in weeks['current'].date_range():
            test_dates.append(day)

        intervals = Interval.objects.filter(rep=rep1)
        self.assertEqual(practices, [
            ((practice, [(setInstance, [(swimmer1, [(rep1, intervals[0])]), (swimmer2, [(rep1, None)])])]), 'monday'),
            ((None, (None, (None, (None, None)))), 'tuesday'),
            ((None, (None, (None, (None, None)))), 'wednesday'),
            ((None, (None, (None, (None, None)))), 'thursday'),
            ((None, (None, (None, (None, None)))), 'friday'),
            ((None, (None, (None, (None, None)))), 'saturday'),
            ((None, (None, (None, (None, None)))), 'sunday'),
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

    def test_calculate_intervals(self):
        """
        Calculates intervals for a set and returns nothing.
        """
        week = test.create_week()
        week.populate()
        team = test.create_team(self.user)
        swimmer1 = test.create_swimmer(team)
        swimmer2 = test.create_swimmer(team, first='Dave', last='Thornton')
        base1_free = test.create_event(swimmer1, 'base free', timedelta(seconds=25))
        base2_free = test.create_event(swimmer2, 'base free', timedelta(seconds=24))

        training_model = test.create_training_model(team)
        training_mult = test.create_training_multiplier(training_model, multiplier=0.07)

        practice = test.create_practice(team, week)
        setInstance = test.create_set(practice, swimmers=[swimmer1, swimmer2])
        rep1 = test.create_rep(setInstance)

        funct.calculate_intervals(setInstance, training_model)
        intervals = Interval.objects.filter(rep=rep1)
        self.assertEqual(intervals[0].swimmer.l_name, 'Gridley')
        self.assertEqual(intervals[1].swimmer.l_name, 'Thornton')
        self.assertEqual(intervals[0].time, timedelta(seconds=55))
        self.assertEqual(intervals[1].time, timedelta(seconds=55))

    def test_get_zipped_set(self):
        """
        Returns list of tuples containing the rep, swimmer, and interval.
        """
        week = test.create_week()
        week.populate()
        team = test.create_team(self.user)
        swimmer1 = test.create_swimmer(team)
        swimmer2 = test.create_swimmer(team, first='Dave', last='Thornton')
        base1_free = test.create_event(swimmer1, 'base free', timedelta(seconds=25))
        base2_free = test.create_event(swimmer2, 'base free', timedelta(seconds=24))

        practice = test.create_practice(team, week)
        setInstance = test.create_set(practice, swimmers=[swimmer1, swimmer2])
        rep1 = test.create_rep(setInstance)

        training_model = test.create_training_model(team)

        funct.calculate_intervals(setInstance, training_model)
        intervals = Interval.objects.filter(rep=rep1)
        set_zip = funct.get_zipped_set(setInstance)

        self.assertEqual(set_zip, [
            (swimmer1, [(rep1, None)]),
            (swimmer2, [(rep1, None)]),
        ])

        training_mult = test.create_training_multiplier(training_model, multiplier=0.07)


        funct.calculate_intervals(setInstance, training_model)
        intervals = Interval.objects.filter(rep=rep1)
        set_zip = funct.get_zipped_set(setInstance)

        self.assertEqual(set_zip, [
            (swimmer1, [(rep1, intervals[0])]),
            (swimmer2, [(rep1, intervals[1])]),
        ])

    def test_get_swimmer_records(self):
        """
        Returns a swimmer's top time in each event or None.
        """
        team = test.create_team(self.user)
        swimmer = test.create_swimmer(team)
        event1 = test.create_event(swimmer, '50 free', timedelta(seconds=22.96))
        event2 = test.create_event(swimmer, '50 free', timedelta(seconds=22.32))
        event3 = test.create_event(swimmer, '100 free', timedelta(seconds=49.86))
        event4 = test.create_event(swimmer, '100 free', timedelta(seconds=50.58))
        event5 = test.create_event(swimmer, '200 free', timedelta(seconds=124.04))

        records = funct.get_swimmer_records(swimmer)
        times = []
        for record in records:
            if record[1]:
                times.append(record[1].time.total_seconds())
            else:
                times.append(None)

        self.assertEqual(records, [
            ('50 Freestyle', event2),
            ('100 Freestyle', event3),
            ('200 Freestyle', event5),
            ('500 Freestyle', None),
            ('1000 Freestyle', None),
            ('50 Backstroke', None),
            ('100 Backstroke', None),
            ('200 Backstroke', None),
            ('50 Breaststroke', None),
            ('100 Breaststroke', None),
            ('200 Breaststroke', None),
            ('50 Butterfly', None),
            ('100 Butterfly', None),
            ('200 Butterfly', None),
            ('100 IM', None),
            ('200 IM', None),
            ('400 IM', None),
        ])
        self.assertEqual(times, [22.32, 49.86, 124.04, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None])

    def test_team_records(self):
        """
        Returns the team's top time in each event or None for both men and women.
        """
        team = test.create_team(self.user)
        swimmer1 = test.create_swimmer(team)
        swimmer2 = test.create_swimmer(team, first='Jane', last='Doe', gender='F')
        event1 = test.create_event(swimmer1, '50 free', timedelta(seconds=22.96))
        event2 = test.create_event(swimmer1, '50 free', timedelta(seconds=22.32))
        event3 = test.create_event(swimmer2, '50 free', timedelta(seconds=25.14))
        event4 = test.create_event(swimmer1, '100 free', timedelta(seconds=49.86))
        event5 = test.create_event(swimmer2, '100 free', timedelta(seconds=54.85))

        records = funct.get_team_records(team)

        self.assertEqual(records, [
            ('50 Freestyle', event2, event3),
            ('100 Freestyle', event4, event5),
            ('200 Freestyle', None, None),
            ('500 Freestyle', None, None),
            ('1000 Freestyle', None, None),
            ('50 Backstroke', None, None),
            ('100 Backstroke', None, None),
            ('200 Backstroke', None, None),
            ('50 Breaststroke', None, None),
            ('100 Breaststroke', None, None),
            ('200 Breaststroke', None, None),
            ('50 Butterfly', None, None),
            ('100 Butterfly', None, None),
            ('200 Butterfly', None, None),
            ('100 IM', None, None),
            ('200 IM', None, None),
            ('400 IM', None, None),
        ])
