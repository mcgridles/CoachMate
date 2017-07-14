from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import teams.tests.test_setup as test

class TestTeamListView(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_team_list_with_no_teams(self):
        """
        No teams are displayed if the queryset is empty.
        """
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('teams:team_list'))
        self.assertQuerysetEqual(response.context['team_list'], [])
        self.assertContains(response, 'No teams yet.')

    def test_team_list_with_teams(self):
        """
        Teams are displayed in a table.
        """
        self.client.login(username='user1', password='password')
        test.create_team(user=self.user1)
        response = self.client.get(reverse('teams:team_list'))
        self.assertQuerysetEqual(
            response.context['team_list'],
            ['<Team: Northeastern University>'],
        )
        self.assertContains(response, 'Northeastern University')

    def test_multiple_teams(self):
        """
        Teams are displayed in alphabetical order.
        """
        self.client.login(username='user1', password='password')
        test.create_team(user=self.user1)
        test.create_team(user=self.user1, name='University of Kansas')
        response = self.client.get(reverse('teams:team_list'))
        self.assertQuerysetEqual(
            response.context['team_list'],
            ['<Team: Northeastern University>', '<Team: University of Kansas>'],
        )

    def test_multiple_users_with_teams(self):
        """
        Different users have different team data.
        """
        self.client.login(username='user1', password='password')
        test.create_team(user=self.user1)
        test.create_team(user=self.user2, name='University of Kansas')
        response = self.client.get(reverse('teams:team_list'))
        self.assertQuerysetEqual(
            response.context['team_list'],
            ['<Team: Northeastern University>'],
        )
        self.assertContains(response, 'Northeastern University')
        self.assertNotContains(response, 'University of Kansas')


class TestSwimmerListView(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_swimmer_list_with_no_swimmers(self):
        """
        No swimmers are displayed if the queryset is empty.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        response = self.client.get(reverse('teams:swimmer_list', kwargs={'abbr': team.abbr}))
        self.assertQuerysetEqual(response.context['swimmer_list'], [])
        self.assertContains(response, 'Northeastern University')
        self.assertNotContains(response, 'Henry Gridley')

    def test_swimmer_list_with_swimmers(self):
        """
        Swimmers are displayed in a table.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        test.create_swimmer(team=team)
        response = self.client.get(reverse('teams:swimmer_list', kwargs={'abbr': team.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: Gridley>'],
        )
        self.assertContains(response, 'Gridley')

    def test_multiple_swimmers(self):
        """
        Swimmer are displayed in alphabetical order.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        test.create_swimmer(team=team)
        test.create_swimmer(team=team, last='Pinkes')
        response = self.client.get(reverse('teams:swimmer_list', kwargs={'abbr': team.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: Gridley>', '<Swimmer: Pinkes>'],
        )

    def test_multiple_users_with_swimmers(self):
        """
        Different users have different swimmer data.
        """
        self.client.login(username='user1', password='password')
        team1 = test.create_team(user=self.user1)
        test.create_swimmer(team=team1)
        team2 = test.create_team(user=self.user2)
        test.create_swimmer(team=team2, last='Pinkes')
        response = self.client.get(reverse('teams:swimmer_list', kwargs={'abbr': team1.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: Gridley>'],
        )
        self.assertContains(response, 'Northeastern University')
        self.assertNotContains(response, 'University of Kansas')


class TestWritePracticeView(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()


class TestPracticeScheduleView(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()


class TestDeleteModelsViews(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')

    def tearDown(self):
        self.user1.delete()

    def test_delete_team(self):
        """
        Deletes a team.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        response = self.client.get(reverse(
                'teams:deleteTeam',
                kwargs={'abbr': team.abbr}),
            follow=True)
        self.assertQuerysetEqual(response.context['team_list'], [])


    def test_delete_swimmer(self):
        """
        Deletes a swimmer.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        swimmer = test.create_swimmer(team=team)
        response = self.client.get(reverse(
                'teams:deleteSwimmer',
                kwargs={'abbr': team.abbr, 's_id': swimmer.id}),
            follow=True)
        self.assertQuerysetEqual(response.context['swimmer_list'], [])

    def test_delete_practice(self):
        """
        Deletes a practice.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        week = test.create_week()
        week.populate()
        practice = test.create_practice(team=team, week=week)
        response = self.client.get(reverse(
                'teams:deletePractice',
                kwargs={'abbr': team.abbr, 'p_id': practice.id}),
            follow=True)
        self.assertEqual(response.context['practices'][0], None)
