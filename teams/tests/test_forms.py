from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

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

    def test_team_form_init(self):
        """
        TeamForm can take a user as an argument.
        """
        TeamForm(user=self.user)
        TeamForm()

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

    def test_swimmer_form_init(self):
        """
        SwimmerForm can take a team as an argument.
        """
        SwimmerForm(team=self.team)
        SwimmerForm()

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


class TestEventForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        team = test.create_team(user=user)
        self.swimmer = test.create_swimmer(team)

    def tearDown(self):
        self.swimmer.delete()

    def test_event_form_init(self):
        """
        EventForm can take a swimmer as an argument.
        """
        EventForm()
        EventForm(swimmer=self.swimmer)

    def test_event_form_valid_data(self):
        """
        EventForm takes an event, time, and date to validate.
        """
        form = EventForm({
            'event': '50 free',
            'time': timedelta(seconds=22.32),
            'date': date(2017,4,9),
        }, swimmer=self.swimmer)
        self.assertTrue(form.is_valid())
        event = form.save()
        self.assertEqual(event.event, '50 free')
        self.assertEqual(event.time, timedelta(seconds=22.32))
        self.assertEqual(event.date, date(2017,4,9))
        self.assertEqual(event.swimmer, self.swimmer)

    def test_event_form_invalid_data(self):
        """
        An event, time, and date are needed to validate.
        """
        form = EventForm({}, swimmer=self.swimmer)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'event': ['This field is required.'],
            'time': ['This field is required.'],
            'date': ['This field is required.'],
        })


class TestPracticeForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        self.team = test.create_team(user=user)
        self.week = test.create_week()

    def tearDown(self):
        self.team.delete()
        self.week.delete()

    def test_practice_form_init(self):
        """
        PracticeForm can take a week and team as an argument
        """
        PracticeForm(team=self.team, week=self.week)
        PracticeForm()

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
        self.team = test.create_team(user=user)
        week = test.create_week()
        self.practice = test.create_practice(self.team, week)

    def tearDown(self):
        self.team.delete()
        self.practice.delete()

    def test_set_form_init(self):
        """
        SetForm can take a practice and/or a team as an argument.
        """
        SetForm(practice=self.practice)
        SetForm(team=self.team)
        SetForm(practice=self.practice, team=self.team)
        SetForm()

    def test_set_form_valid_data(self):
        """
        SetForm takes a focus, group, pace, and order to validate.
        """
        form = SetForm({
            'pace': 'train',
            'focus': 'warmup',
            'order': 1,
            'group': 'team',
        }, practice=self.practice)
        self.assertTrue(form.is_valid())
        setInstance = form.save()
        self.assertEqual(setInstance.focus, 'warmup')
        self.assertEqual(setInstance.order, 1)
        self.assertEqual(setInstance.practice_id, self.practice)
        self.assertEqual(setInstance.group, 'team')
        self.assertQuerysetEqual(setInstance.swimmers.all(), [])

    def test_set_form_invalid_data(self):
        """
        SetForm will not validate without a focus and order.
        """
        form = SetForm({}, practice=self.practice)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'pace': ['This field is required.'],
            'focus': ['This field is required.'],
            'order': ['This field is required.'],
            'group': ['This field is required.'],
        })


class TestRepForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        team = test.create_team(user=user)
        week = test.create_week()
        practice = test.create_practice(team, week)
        self.test_set = test.create_set(practice=practice)

    def tearDown(self):
        self.test_set.delete()

    def test_rep_form_init(self):
        """
        RepForm takes no arguments.
        """
        RepForm()

    def test_rep_form_valid_data(self):
        """
        RepForm takes a number, distance, stroke to validate.
        """
        form = RepForm({
            'num': 1,
            'distance': 100,
            'stroke': 'free',
        })
        self.assertTrue(form.is_valid())
        repInstance = form.save(commit=False)
        repInstance.set_id = self.test_set
        repInstance.save()
        self.assertEqual(repInstance.num, 1)
        self.assertEqual(repInstance.distance, 100)
        self.assertEqual(repInstance.stroke, 'free')
        self.assertEqual(repInstance.set_id, self.test_set)

    def test_rep_form_invalid_data(self):
        """
        RepForm will not validate without a number, distance, and stroke.
        """
        form = RepForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'num': ['This field is required.'],
            'distance': ['This field is required.'],
            'stroke': ['This field is required.'],
        })


class TestTrainingForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        self.team = test.create_team(user=user)

    def tearDown(self):
        self.team.delete()

    def test_training_form_init(self):
        """
        TrainingForm takes no arguments.
        """
        TrainingForm()

    def test_training_form_valid_data(self):
        """
        TrainingForm takes a team to validate.
        """
        form = TrainingForm({
            'team': self.team.id,
        })
        self.assertTrue(form.is_valid())
        trainingInstance = form.save()
        self.assertEqual(trainingInstance.team, self.team)

    def test_training_form_invalid_data(self):
        """
        TrainingForm will not validate without a team.
        """
        form = TrainingForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'team': ['This field is required.'],
        })


class TestMultiplierForm(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        team = test.create_team(user=user)
        self.training_model = test.create_training_model(team)

    def tearDown(self):
        self.training_model.delete()

    def test_multiplier_form_init(self):
        """
        MultiplierForm takes no arguments.
        """
        MultiplierForm()

    def test_multiplier_form_valid_data(self):
        """
        MultiplierForm takes a focus and multiplier to validate.
        """
        form = MultiplierForm({
            'focus': 'warmup',
            'multiplier': 1,
        })
        self.assertTrue(form.is_valid())
        multiplierInstance = form.save(commit=False)
        multiplierInstance.training_model = self.training_model
        multiplierInstance.save()
        self.assertEqual(multiplierInstance.focus, 'warmup')
        self.assertEqual(multiplierInstance.multiplier, '1')
        self.assertEqual(multiplierInstance.training_model, self.training_model)

    def test_multiplier_form_invalid_data(self):
        """
        MultiplierForm will not validate without a focus and multiplier.
        """
        form = MultiplierForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'focus': ['This field is required.'],
            'multiplier': ['This field is required.'],
        })
