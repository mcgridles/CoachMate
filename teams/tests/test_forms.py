from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless

from django.test import TestCase
from django.urls import reverse

from teams.forms import *
import teams.tests.test_setup as test
from teams.models import Team


class TestTeamForm(TestCase):
    def setUp(self):
        self.user = test.create_user('user', 'password')

    def tearDown(self):
        self.user.delete()

    def test_team_form_init_with_no_user(self):
        """
        KeyError raised if no user is passed to the form.
        """
        self.assertRaises(KeyError, TeamForm, None)

    def test_team_form_init(self):
        """
        TeamForm takes a user as an argument.
        """
        TeamForm(user=self.user)

    def test_team_form_valid_data(self):
        """
        TeamForm takes a team name, abbreviation, and a user to validate.
        """
        form = TeamForm({
            'name': 'Northeastern University',
            'abbr': 'NUSC',
        }, user=self.user)
        self.assertTrue(form.is_valid())
        team = form.save()
        self.assertEqual(team.name, 'Northeastern University')
        self.assertEqual(team.abbr, 'NUSC')
        self.assertEqual(team.user, self.user)

    def test_team_form_invalid_data(self):
        """
        TeamForm will not validate without a team name or abbreviation.
        """
        form = TeamForm({}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
            'abbr': ['This field is required.'],
        })


class TestSwimmerForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        self.team = test.create_team(user=user)

    def tearDown(self):
        self.team.delete()

    def test_swimmer_form_init_with_no_team(self):
        """
        KeyError raised if no team is passed to the form.
        """
        self.assertRaises(KeyError, SwimmerForm, None)

    def test_swimmer_form_init(self):
        """
        SwimmerForm takes a team as an argument.
        """
        SwimmerForm(team=self.team)

    def test_swimmer_form_valid_data(self):
        """
        SwimmerForm takes a first name, last name, gender, and a team to validate.
        """
        form = SwimmerForm({
            'f_name': 'Henry',
            'l_name': 'Gridley',
            'gender': 'M',
        }, team=self.team)
        self.assertTrue(form.is_valid())
        swimmer = form.save()
        self.assertEqual(swimmer.f_name, 'Henry')
        self.assertEqual(swimmer.l_name, 'Gridley')
        self.assertEqual(swimmer.gender, 'M')
        self.assertEqual(swimmer.team, self.team)

    def test_swimmer_form_invalid_data(self):
        """
        SwimmerForm will not validate without a first name, last name, or gender.
        """
        form = SwimmerForm({}, team=self.team)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'f_name': ['This field is required.'],
            'l_name': ['This field is required.'],
            'gender': ['This field is required.'],
        })


class TestSetForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        self.team = test.create_team(user=user)
        self.week = test.create_week()

    def tearDown(self):
        self.team.delete()
        self.week.delete()

    def test_practice_form_init_with_no_team(self):
        """
        KeyError raised if no week and team is passed to the form.
        """
        self.assertRaises(KeyError, PracticeForm, None)

    def test_practice_form_init(self):
        """
        PracticeForm takes a week and team as an argument
        """
        PracticeForm(team=self.team, week=self.week)

    def test_practice_form_valid_data(self):
        """
        PracticeForm takes a weekday to validate.
        """
        form = PracticeForm({
            'weekday': 'monday',
        }, team=self.team, week=self.week)
        self.assertTrue(form.is_valid())
        practice = form.save()
        self.assertEqual(practice.weekday, 'monday')
        self.assertEqual(practice.team, self.team)
        self.assertEqual(practice.week_id, self.week)

    def test_practice_form_invalid_data(self):
        """
        SetForm will not validate without a focus and order.
        """
        form = PracticeForm({}, team=self.team, week=self.week)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'weekday': ['This field is required.'],
        })


class TestSetForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        team = test.create_team(user=user)
        week = test.create_week()
        self.practice = test.create_practice(team, week)

    def tearDown(self):
        self.practice.delete()

    def test_set_form_init_with_no_team(self):
        """
        KeyError raised if no practice is passed to the form.
        """
        self.assertRaises(KeyError, SetForm, None)

    def test_set_form_init(self):
        """
        SetForm takes a practice as an argument
        """
        SetForm(practice=self.practice)

    def test_set_form_valid_data(self):
        """
        SetForm takes a focus and an order to validate.
        """
        form = SetForm({
            'focus': 'warmup',
            'order': 1,
        }, practice=self.practice)
        self.assertTrue(form.is_valid())
        set = form.save()
        self.assertEqual(set.focus, 'warmup')
        self.assertEqual(set.order, 1)
        self.assertEqual(set.practice_id, self.practice)

    def test_set_form_invalid_data(self):
        """
        SetForm will not validate without a focus and order.
        """
        form = SetForm({}, practice=self.practice)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'focus': ['This field is required.'],
            'order': ['This field is required.'],
        })
