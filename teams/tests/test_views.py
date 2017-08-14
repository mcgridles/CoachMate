from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.urls import reverse

import teams.tests.test_setup as test
from teams.models import *
import teams.functions as funct

# Team list

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
        response = self.client.get(reverse('teams:teamList'))
        self.assertQuerysetEqual(response.context['team_list'], [])
        self.assertContains(response, 'No teams yet.')

    def test_team_list_with_teams(self):
        """
        Teams are displayed in a table.
        """
        self.client.login(username='user1', password='password')
        test.create_team(user=self.user1)
        response = self.client.get(reverse('teams:teamList'))
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
        response = self.client.get(reverse('teams:teamList'))
        self.assertQuerysetEqual(
            response.context['team_list'],
            ['<Team: Northeastern University>', '<Team: University of Kansas>'],
        )

    def test_multiple_users_with_teams(self):
        """
        Only the teams belonging to the logged in user will be displayed.
        """
        self.client.login(username='user1', password='password')
        test.create_team(user=self.user1)
        test.create_team(user=self.user2, name='University of Kansas')
        response = self.client.get(reverse('teams:teamList'))
        self.assertQuerysetEqual(
            response.context['team_list'],
            ['<Team: Northeastern University>'],
        )
        self.assertContains(response, 'Northeastern University')
        self.assertNotContains(response, 'University of Kansas')

        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:teamList'))
        self.assertQuerysetEqual(
            response.context['team_list'],
            ['<Team: University of Kansas>'],
        )
        self.assertNotContains(response, 'Northeastern University')
        self.assertContains(response, 'University of Kansas')

    def test_team_form_input(self):
        """
        Team form validation requires a team name and abbreviation.
        """
        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('teams:teamList'), {
                'name': 'Northeastern University Swim Club',
                'abbr': 'NUSC',
                'region': 'US-NE',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NUSC')

    def test_team_form_errors(self):
        """
        Errors displayed if invalid information is entered.
        """
        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('teams:teamList'), {
                'abbr': 'NUSC',
                'region': 'US-NE',
            },
            follow=True)
        self.assertEqual(response.context['team_form'].errors, {
            'name': ['This field is required.']
        })


# Team Records

class TestTeamRecordsView(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        self.team = test.create_team(user)

    def tearDown(self):
        self.team.delete()

    def test_team_records_no_times(self):
        """
        Times are blank if there are no events for the given team.
        """
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('teams:teamRecords', kwargs={
                'abbr': self.team.abbr,
            })
        )
        self.assertContains(response, 'Records')
        self.assertContains(response, 'Men')
        self.assertContains(response, 'Women')
        self.assertContains(response, '--')
        self.assertNotContains(response, '00:22.32')

    def test_team_records_with_times(self):
        """
        The fastest time in each event is shown.
        """
        swimmer = test.create_swimmer(self.team)
        event1 = test.create_event(swimmer, '50 free', timedelta(seconds=22.32))
        event2 = test.create_event(swimmer, '50 free', timedelta(seconds=22.96))
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('teams:teamRecords', kwargs={
                'abbr': self.team.abbr,
            })
        )
        self.assertContains(response, '--')
        self.assertContains(response, '00:22.32')
        self.assertNotContains(response, '00:22.96')

    def test_team_records_with_times(self):
        """
        The fastest time in each event is shown for men and women.
        """
        swimmer1 = test.create_swimmer(self.team)
        swimmer2 = test.create_swimmer(self.team, first='Jane', last='Doe', gender='F')
        event1 = test.create_event(swimmer1, '50 free', timedelta(seconds=22.32))
        event2 = test.create_event(swimmer1, '50 free', timedelta(seconds=22.96))
        event3 = test.create_event(swimmer2, '50 free', timedelta(seconds=23.51))
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('teams:teamRecords', kwargs={
                'abbr': self.team.abbr,
            })
        )
        #print response
        self.assertContains(response, '--')
        self.assertContains(response, '00:22.32')
        self.assertContains(response, '00:23.51')
        self.assertNotContains(response, '00:22.96')


# Swimmer list

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
        response = self.client.get(reverse('teams:swimmerList', kwargs={'abbr': team.abbr}))
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
        response = self.client.get(reverse('teams:swimmerList', kwargs={'abbr': team.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: Henry Gridley>'],
        )
        self.assertContains(response, 'Gridley')

    def test_multiple_swimmers(self):
        """
        Swimmer are displayed in alphabetical order.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        test.create_swimmer(team=team)
        test.create_swimmer(team=team, first='Samantha', last='Pinkes')
        response = self.client.get(reverse('teams:swimmerList', kwargs={'abbr': team.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: Henry Gridley>', '<Swimmer: Samantha Pinkes>'],
        )

    def test_multiple_users_with_swimmers(self):
        """
        Only the swimmers belonging to the logged in user will be displayed.
        """
        self.client.login(username='user1', password='password')
        team1 = test.create_team(user=self.user1)
        test.create_swimmer(team=team1)
        team2 = test.create_team(user=self.user2)
        test.create_swimmer(team=team2, first='David', last='Thornton')
        response = self.client.get(reverse('teams:swimmerList', kwargs={'abbr': team1.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: Henry Gridley>'],
        )
        self.assertContains(response, 'Northeastern University')
        self.assertContains(response, 'Gridley')
        self.assertNotContains(response, 'Thornton')


        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:swimmerList', kwargs={'abbr': team2.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: David Thornton>'],
        )
        self.assertContains(response, 'Northeastern University')
        self.assertContains(response, 'Thornton')
        self.assertNotContains(response, 'Gridley')

    def test_swimmer_form_input(self):
        """
        Swimmer form validation requires a first name, last name, and gender.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        response = self.client.post(reverse('teams:swimmerList', kwargs={
                'abbr': team.abbr
            }),
            {
                'f_name': 'Henry',
                'l_name': 'Gridley',
                'gender': 'M',
                'swimmer_create': 'Submit',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gridley')

    def test_swimmer_form_input_include_birth_date(self):
        """
        Swimmer age can be calculated based on a birth date.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        response = self.client.post(reverse('teams:swimmerList', kwargs={
                'abbr': team.abbr
            }),
            {
                'f_name': 'Henry',
                'l_name': 'Gridley',
                'gender': 'M',
                'birth_date': '09/21/1996',
                'swimmer_create': 'Submit',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gridley')
        self.assertEqual(response.context['swimmer_list'].get(l_name='Gridley').age, 20)

    def test_swimmer_form_errors(self):
        """
        Errors displayed if invalid information is entered.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        response = self.client.post(reverse('teams:swimmerList', kwargs={
                'abbr': team.abbr
            }),
            {
                'gender': 'M',
                'birth_date': '09/21/1996',
                'swimmer_create': 'Submit',
            },
            follow=True)
        self.assertEqual(response.context['swimmer_form'].errors, {
            'l_name': ['This field is required.'],
            'f_name': ['This field is required.'],
        })

    def test_edit_team_form(self):
        """
        Team models can be edited from their swimmerList page.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        response = self.client.post(reverse('teams:swimmerList', kwargs={
                'abbr': team.abbr
            }),
            {
                'name': 'University of Kansas',
                'abbr': 'KUSC',
                'team_edit': 'Submit',
            },
            follow=True)
        self.assertContains(response, 'University of Kansas')

    def test_roster_upload(self):
        """
        Team Manager rosters can be uploaded in a .zip file.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(self.user1)
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/NUSC-NE-Roster003.zip') as f:
            response = self.client.post(reverse('teams:swimmerList', kwargs={
                    'abbr': team.abbr
                }),
                {
                    'zip_file': f,
                    'upload': 'Submit'
                },
                follow=True
            )

            swimmers = [
                '<Swimmer: Abel>',
                '<Swimmer: Alkislar>',
                '<Swimmer: Angotti>',
                '<Swimmer: Armstrong>',
                '<Swimmer: Asai-Sarris>',
                '<Swimmer: Banak>',
                '<Swimmer: Barlow>',
                '<Swimmer: Barnes>',
                '<Swimmer: Bartlett>',
                '<Swimmer: Bauer>',
                '<Swimmer: Behar>',
                '<Swimmer: Berger>',
                '<Swimmer: Bissonnette>',
                '<Swimmer: Bloom>',
                '<Swimmer: Bogatko>',
                '<Swimmer: Chen>',
                '<Swimmer: Cheng>',
                '<Swimmer: Coghlan>',
                '<Swimmer: Coreno>',
                '<Swimmer: DeLiberti>',
                '<Swimmer: Dottinger>',
                '<Swimmer: Doyle>',
                '<Swimmer: Elmaarouf>',
                '<Swimmer: Fleischer>',
                '<Swimmer: Foley>',
                '<Swimmer: Fong>',
                '<Swimmer: Formica>',
                '<Swimmer: Fritzinger>',
                '<Swimmer: Furuta>',
                '<Swimmer: Galus>',
                '<Swimmer: Garber>',
                '<Swimmer: Greene>',
                '<Swimmer: Gridley>',
                '<Swimmer: Harris>',
                '<Swimmer: Haviland>',
                '<Swimmer: Heath>',
                '<Swimmer: Hoang>',
                '<Swimmer: Jaisle>',
                '<Swimmer: Kenyon>',
                '<Swimmer: Landon>',
                '<Swimmer: Laundry>',
                '<Swimmer: Lefler>',
                '<Swimmer: Lenney>',
                '<Swimmer: Leopold>',
                '<Swimmer: Lin>',
                '<Swimmer: Mack>',
                '<Swimmer: Manetti>',
                '<Swimmer: McCollister>',
                '<Swimmer: McCord>',
                '<Swimmer: McCrobie>',
                '<Swimmer: McGann>',
                '<Swimmer: Miller>',
                '<Swimmer: Monasterio>',
                '<Swimmer: Movchan>',
                '<Swimmer: Murphy>',
                '<Swimmer: Niemi>',
                '<Swimmer: Nikopoulos>',
                '<Swimmer: Noble>',
                '<Swimmer: Nozhenko>',
                "<Swimmer: O'Donnell>",
                '<Swimmer: Papes>',
                '<Swimmer: Perez>',
                '<Swimmer: Philbrick>',
                '<Swimmer: Pinkes>',
                '<Swimmer: Plummer>',
                '<Swimmer: Regulapati>',
                '<Swimmer: Renaud>',
                '<Swimmer: Shi>',
                '<Swimmer: Smolyar>',
                '<Swimmer: Soucy>',
                '<Swimmer: Thornton>',
                '<Swimmer: Toppazzini>',
                '<Swimmer: Tou>',
                '<Swimmer: Van Winkle>',
            ]
            new_swimmers = []
            for swimmer in team.swimmer_set.all():
                new_swimmers.append('<Swimmer: ' + swimmer.l_name + '>')
            self.assertEqual(new_swimmers, swimmers)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Roster imported')

    def test_roster_upload_error(self):
        """
        An error message is displayed if swimmers can't be uploaded, or files can't
        be found.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(self.user1)
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/fftlighttest-Roster.zip') as f:
            response = self.client.post(reverse('teams:swimmerList', kwargs={
                    'abbr': team.abbr
                }),
                {
                    'zip_file': f,
                    'upload': 'Submit'
                },
                follow=True
            )
            self.assertQuerysetEqual(team.swimmer_set.all(), [])
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Couldn&#39;t find .CL2 or .HY3 file in zip file')

    def test_roster_and_results_upload(self):
        """
        Loads a team roster from a zip file then loads meet results for that team
        from a different zip file.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(self.user1)
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/NUSC-NE-Roster003.zip', 'r') as f:
            response = self.client.post(reverse('teams:swimmerList', kwargs={
                    'abbr': team.abbr
                }),
                {
                    'zip_file': f,
                    'upload': 'Submit'
                },
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Roster imported')

        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/RED-NE-Results005.zip', 'r') as f:
            response = self.client.post(reverse('teams:swimmerList', kwargs={
                    'abbr': team.abbr
                }),
                {
                    'zip_file': f,
                    'upload': 'Submit'
                },
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Results imported')

        swimmers = Swimmer.objects.all()
        events = Event.objects.all()
        self.assertEqual(len(swimmers), 74)
        self.assertEqual(len(events), 113)

    def test_invalid_file_upload(self):
        """
        An error message is displayed if the file is not named correctly.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(self.user1)
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/CFILE01.CL2') as f:
            response = self.client.post(reverse('teams:swimmerList', kwargs={
                    'abbr': team.abbr
                }),
                {
                    'zip_file': f,
                    'upload': 'Submit'
                },
                follow=True
            )
            self.assertQuerysetEqual(team.swimmer_set.all(), [])
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'ERROR: File must be in ZIP format')


# Swimmer Detail

class TestSwimmerDetailView(TestCase):
    def setUp(self):
        self.user = test.create_user('user', 'password')
        self.team = test.create_team(user=self.user)

    def tearDown(self):
        self.user.delete()
        self.team.delete()

    def test_swimmer_page(self):
        """
        Each swimmer has their own page that contains bio information.
        """
        self.client.login(username='user', password='password')
        swimmer = test.create_swimmer(self.team)
        swimmer.set_age()
        response = self.client.get(reverse('teams:swimmerDetail', kwargs={
                'abbr': self.team.abbr,
                's_id': swimmer.id,
            })
        )
        self.assertEqual(response.context['swimmer'].l_name, 'Gridley')
        self.assertContains(response, 'Henry Gridley')

    def test_swimmer_edit(self):
        """
        Swimmers can be edited on their personal page.
        """
        self.client.login(username='user', password='password')
        swimmer = test.create_swimmer(self.team)
        swimmer.set_age()
        response = self.client.get(reverse('teams:swimmerDetail', kwargs={
                'abbr': self.team.abbr,
                's_id': swimmer.id,
            }),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Henry Gridley')

        response = self.client.post(reverse('teams:swimmerDetail', kwargs={
                'abbr': self.team.abbr,
                's_id': swimmer.id,
            }),
            {
                'f_name': 'Dave',
                'l_name': 'Thornton',
                'gender': 'M',
                'edit_swimmer': 'Submit',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dave Thornton')

    def test_event_input(self):
        """
        EventForms take an event, time, and date to validate, and create an event
        associated with the current swimmer.
        """
        self.client.login(username='user', password='password')
        swimmer = test.create_swimmer(self.team)
        swimmer.set_age()
        response = self.client.post(reverse('teams:swimmerDetail', kwargs={
                'abbr': self.team.abbr,
                's_id': swimmer.id,
            }),
            {
                'event': '50 free',
                'time': timedelta(seconds=22.32),
                'date': date(2017,4,9),
                'add_event': 'Submit',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Henry Gridley')

    @skip('Works but creates unwanted extra image file in /media')
    def test_swimmer_form_image_upload(self):
        """
        Only .png and .jpg images are valid.
        """
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/CFILE01.CL2', 'rb') as f:
            self.client.login(username='user', password='password')
            swimmer = test.create_swimmer(self.team)
            swimmer.set_age()
            response = self.client.post(reverse('teams:swimmerDetail', kwargs={
                    'abbr': self.team.abbr,
                    's_id': swimmer.id,
                }),
                {
                    'f_name': 'Henry',
                    'l_name': 'Gridley',
                    'gender': 'M',
                    'picture': f,
                    'edit_swimmer': 'Submit',
                },
                follow=True
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(
                response,
                'Upload a valid image. The file you uploaded was either not an image or a corrupted image.'
            )

        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/background.png', 'rb') as f:
            self.client.login(username='user', password='password')
            swimmer = test.create_swimmer(self.team)
            swimmer.set_age()
            response = self.client.post(reverse('teams:swimmerDetail', kwargs={
                    'abbr': self.team.abbr,
                    's_id': swimmer.id,
                }),
                {
                    'f_name': 'Henry',
                    'l_name': 'Gridley',
                    'gender': 'M',
                    'picture': f,
                    'edit_swimmer': 'Submit',
                },
                follow=True
            )
            swimmer.refresh_from_db()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(swimmer.picture.name[0:10], 'background')


# Write practices

class TestWritePracticeView(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_write_practice_with_no_sets(self):
        """
        Only panel headings are displayed when no sets have been written.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        practice = test.create_practice(team, week)
        response = self.client.get(reverse('teams:writePractice', kwargs={
                'abbr': team.abbr,
                'p_id': practice.id
            })
        )
        self.assertEqual(response.context['practice'].weekday, 'monday')
        self.assertQuerysetEqual(response.context['set_list'], [])
        self.assertContains(response, 'Create a Set')

    def test_write_practice_with_sets(self):
        """
        Sets are displayed in order with all reps and headings.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        practice = test.create_practice(team, week)
        set1 = test.create_set(practice=practice)
        rep1 = test.create_rep(_set=set1)
        set2 = test.create_set(practice, 'sprint', 2, 2)
        rep2 = test.create_rep(set2, 4, 25, 'fly')
        rep3 = test.create_rep(set2, 8, 200, 'back')
        response = self.client.get(reverse('teams:writePractice', kwargs={
                'abbr': team.abbr,
                'p_id': practice.id
            })
        )
        self.assertEqual(response.context['practice'].weekday, 'monday')
        self.assertQuerysetEqual(
            response.context['set_list'],
            ['<Set: warmup>', '<Set: sprint>'],
            ordered=False,
        )
        self.assertContains(response, 'Create a Set')
        self.assertContains(response, 'Warmup')
        self.assertContains(response, 'Sprint')
        self.assertContains(response, 'free')
        self.assertContains(response, 'fly')
        self.assertContains(response, 'back')

    def test_multiple_users_with_sets(self):
        """
        Only sets belonging to the logged in user will be displayed.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team1 = test.create_team(user=self.user1)
        team2 = test.create_team(user=self.user2)
        practice1 = test.create_practice(team1, week)
        practice2 = test.create_practice(team2, week)
        set1 = test.create_set(practice=practice1)
        rep1 = test.create_rep(_set=set1)
        set2 = test.create_set(practice2, 'sprint', 2, 2)
        rep2 = test.create_rep(set2, 4, 25, 'fly')
        rep3 = test.create_rep(set2, 8, 200, 'back')
        response = self.client.get(reverse('teams:writePractice', kwargs={
                'abbr': team1.abbr,
                'p_id': practice1.id
            })
        )
        self.assertQuerysetEqual(
            response.context['set_list'],
            ['<Set: warmup>']
        )

        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:writePractice', kwargs={
                'abbr': team2.abbr,
                'p_id': practice2.id
            })
        )
        self.assertQuerysetEqual(
            response.context['set_list'],
            ['<Set: sprint>']
        )

    def test_practice_form(self):
        """
        Practices can be edited from the set creation page.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        practice = test.create_practice(team, week)
        response = self.client.post(reverse('teams:writePractice', kwargs={
                'abbr': team.abbr,
                'p_id': practice.id,
            }),
            {
                'weekday': 'friday',
                'practice_edit': 'Submit',
            },
            follow=True)
        self.assertEqual(response.context['practice'].weekday, 'friday')
        self.assertContains(response, 'Friday')

    def test_write_practice_set_form(self):
        """
        Set form data is cleaned and used to create a new Set instance.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        practice = test.create_practice(team, week)

        training_model = test.create_training_model(team)
        warmup_mult = test.create_training_multiplier(training_model, multiplier=0.07)

        swimmer1 = test.create_swimmer(team=team)
        base1 = test.create_event(swimmer=swimmer1, event='base free', time=timedelta(seconds=25))
        swimmer2 = test.create_swimmer(team=team, first='David', last='Thornton')
        base2 = test.create_event(swimmer=swimmer2, event='base free', time=timedelta(seconds=24))
        response = self.client.post(reverse('teams:writePractice', kwargs={
                'abbr': team.abbr,
                'p_id': practice.id,
            }),
            {
                'focus': 'warmup',
                'repeats': 2,
                'order': 1,
                'pace': 'train',
                'form-0-num': 4,
                'form-0-distance': 100,
                'form-0-stroke': 'free',
                'form-0-rest': timedelta(seconds=10),
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'group': 'team',
                'set_create': 'Submit',
            },
            follow=True
        )
        set_list = Set.objects.all()
        swimmer_set = set_list[0].swimmers.all()
        rep_set = set_list[0].rep_set.all()
        interval_set = Interval.objects.filter(rep=rep_set[0])
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(set_list, ['<Set: warmup>'])
        self.assertContains(response, '4 x 100 free')
        self.assertQuerysetEqual(
            swimmer_set,
            ['<Swimmer: Henry Gridley>', '<Swimmer: David Thornton>'],
            ordered=False
        )

        self.assertEqual(interval_set[0].swimmer.l_name, 'Gridley')
        self.assertEqual(interval_set[1].swimmer.l_name, 'Thornton')
        self.assertEqual(interval_set[0].time, timedelta(seconds=55))
        self.assertEqual(interval_set[1].time, timedelta(seconds=55))


# Practice schedule

class TestPracticeScheduleView(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_schedule_with_no_practices(self):
        """
        Only panel headings are displayed if the queryset is empty.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ,'sunday']
        practices = [(None, (None, (None, (None, None)))) for x in range(7)]
        practices = zip(practices, weekdays)
        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': week.id,
            })
        )
        self.assertEqual(response.context['practices'], practices)
        self.assertContains(response, 'Monday')
        self.assertContains(response, 'Sunday')
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')

    def test_schedule_with_practices_with_rest(self):
        """
        Practices are displayed in the correct panel, rest is displayed instead of
        an interval if rest has been entered.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        swimmer1 = test.create_swimmer(team)
        base_free = test.create_event(swimmer1, event='base free', time=timedelta(seconds=25))
        swimmer2 = test.create_swimmer(team, first='Dave', last='Thornton')

        practice1 = test.create_practice(team, week)
        set1 = test.create_set(practice=practice1, order=23, swimmers=[swimmer1, swimmer2])
        rep1 = test.create_rep(set1, rest=timedelta(seconds=10))
        practice2 = test.create_practice(team, week, weekday='tuesday')
        set2 = test.create_set(practice=practice2, focus='sprint', repeats=2, order=37)
        set3 = test.create_set(practice=practice2, focus='distance', repeats=3, order=38)

        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': week.id,
            })
        )
        self.assertEqual(response.context['practices'][0][0][0].weekday, 'monday')
        self.assertEqual(response.context['practices'][1][0][0].weekday, 'tuesday')
        self.assertEqual(response.context['practices'][2][0], (None, (None, (None, (None, None)))))
        self.assertContains(response, 'Monday')
        self.assertContains(response, 23)
        self.assertContains(response, 37)
        self.assertContains(response, 38)
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')
        self.assertContains(response, '00:10 r')
        self.assertNotContains(response, '00:53')

    def test_schedule_with_practices_no_intervals(self):
        """
        Practices are displayed in the correct panel, intervals are '--'
        if not found.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        swimmer1 = test.create_swimmer(team)
        base_free = test.create_event(swimmer1, event='base free', time=timedelta(seconds=25))
        swimmer2 = test.create_swimmer(team, first='Dave', last='Thornton')

        practice1 = test.create_practice(team, week)
        set1 = test.create_set(practice=practice1, order=23, swimmers=[swimmer1, swimmer2])
        rep1 = test.create_rep(set1)
        practice2 = test.create_practice(team, week, weekday='tuesday')
        set2 = test.create_set(practice=practice2, focus='sprint', repeats=2, order=37)
        set3 = test.create_set(practice=practice2, focus='distance', repeats=3, order=38)

        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': week.id,
            })
        )
        self.assertEqual(response.context['practices'][0][0][0].weekday, 'monday')
        self.assertEqual(response.context['practices'][1][0][0].weekday, 'tuesday')
        self.assertEqual(response.context['practices'][2][0], (None, (None, (None, (None, None)))))
        self.assertContains(response, 'Monday')
        self.assertContains(response, 23)
        self.assertContains(response, 37)
        self.assertContains(response, 38)
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')
        self.assertContains(response, '--')
        self.assertNotContains(response, '00:53')

    def test_schedule_with_practices_and_intervals(self):
        """
        Practices are displayed in the correct panel with intervals.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        swimmer1 = test.create_swimmer(team)
        base_free = test.create_event(swimmer1, event='base free', time=timedelta(seconds=25))
        swimmer2 = test.create_swimmer(team, first='Dave', last='Thornton')

        practice1 = test.create_practice(team, week)
        set1 = test.create_set(practice=practice1, order=23, swimmers=[swimmer1, swimmer2])
        rep1 = test.create_rep(set1)
        practice2 = test.create_practice(team, week, weekday='tuesday')
        set2 = test.create_set(practice=practice2, focus='sprint', repeats=2, order=37)
        set3 = test.create_set(practice=practice2, focus='distance', repeats=3, order=38)

        training_model = test.create_training_model(team)
        training_mult = test.create_training_multiplier(training_model, multiplier=0.07)
        funct.calculate_intervals(set1, training_model)

        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': week.id,
            })
        )
        self.assertEqual(response.context['practices'][0][0][0].weekday, 'monday')
        self.assertEqual(response.context['practices'][1][0][0].weekday, 'tuesday')
        self.assertEqual(response.context['practices'][2][0], (None, (None, (None, (None, None)))))
        self.assertContains(response, 'Monday')
        self.assertContains(response, 23)
        self.assertContains(response, 37)
        self.assertContains(response, 38)
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')
        self.assertContains(response, '00:55')

    def test_multiple_users_with_practices(self):
        """
        Only practices belonging to the logged in user will be displayed.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team1 = test.create_team(user=self.user1)
        team2 = test.create_team(user=self.user2)
        practice1 = test.create_practice(team1, week)
        practice2 = test.create_practice(team2, week, weekday='tuesday')
        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team1.abbr,
                'w_id': week.id
            })
        )
        self.assertEqual(response.context['practices'][0][0][0].weekday, 'monday')
        self.assertEqual(response.context['practices'][1][0], (None, (None, (None, (None, None)))))
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')

        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team2.abbr,
                'w_id': week.id
            })
        )
        self.assertEqual(response.context['practices'][0][0], (None, (None, (None, (None, None)))))
        self.assertEqual(response.context['practices'][1][0][0].weekday, 'tuesday')
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')

    def test_schedule_with_no_weeks(self):
        """
        Current, previous, and next weeks will be created and populated.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': 0,
            })
        )
        current_week = Week.objects.get(present=True)
        previous_week = current_week.get_week(0)
        next_week = current_week.get_week(1)
        self.assertEqual(current_week.monday, funct.get_monday(n=None))
        self.assertEqual(previous_week.monday, funct.get_monday(n=0))
        self.assertEqual(next_week.monday, funct.get_monday(n=1))

    def test_schedule_with_current_week_only(self):
        """
        Previous and next weeks will be created and populated. Current week will
        be returned from a database query.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        week = test.create_week(monday=funct.get_monday(n=None))
        week.populate()
        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': 0,
            })
        )
        current_week = Week.objects.get(present=True)
        previous_week = current_week.get_week(0)
        next_week = current_week.get_week(1)
        self.assertEqual(current_week, week)
        self.assertEqual(previous_week.monday, funct.get_monday(n=0))
        self.assertEqual(next_week.monday, funct.get_monday(n=1))

    def test_schedule_get_next_week(self):
        """
        The next week becomes the 'current' week and another week is created as
        the 'next' week.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        week = test.create_week()
        week.populate()
        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': 0,
            })
        )

        current_week = Week.objects.get(present=True)
        next_week = current_week.get_week(1)

        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': next_week.id,
            })
        )
        self.assertEqual(response.context['current'], next_week)
        self.assertEqual(response.context['previous'], current_week)
        self.assertEqual(
            response.context['next'].monday,
            funct.get_monday(n=1) + relativedelta(days=7)
        )

    def test_practice_form_input(self):
        """
        Practice form validation requires a weekday.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        week = test.create_week()
        response = self.client.post(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': week.id,
            }),
            {
                'weekday': 'monday',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No sets yet')
        self.assertTemplateUsed(response, 'teams/practice_write.html')

    def test_practice_form_errors(self):
        """
        Errors displayed if invalid information is entered.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        week = test.create_week()
        response = self.client.post(reverse('teams:practiceSchedule', kwargs={
                'abbr': team.abbr,
                'w_id': week.id,
            }),
            {},
            follow=True)
        self.assertEqual(response.context['practice_form'].errors, {
            'weekday': ['This field is required.'],
        })


# Create training model

class TestCreateTrainingView(TestCase):
    def setUp(self):
        self.user = test.create_user('user', 'password')

    def tearDown(self):
        self.user.delete()

    def test_create_training_page(self):
        """
        The training model form is displayed on the page (not hidden by a modal).
        """
        self.client.login(username='user', password='password')
        team = test.create_team(user=self.user)
        response = self.client.get(reverse('teams:createTraining', kwargs={
                't_id': 0,
            })
        )
        self.assertContains(response, 'Training Model')

    def test_create_training_form(self):
        """
        Form input creates a training model to be used for interval calculations.
        """
        self.client.login(username='user', password='password')
        team = test.create_team(user=self.user)
        response = self.client.post(reverse('teams:createTraining', kwargs={
                't_id': 0,
            }),
            {
                'team': team.id,
                'form-0-focus': 'warmup',
                'form-0-multiplier': '40%',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'submit': 'Submit',
            },
            follow=True
        )
        training_model = TrainingModel.objects.all()
        multiplier_set = training_model[0].trainingmultiplier_set.all()
        multiplier = multiplier_set[0]
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(training_model, ['<TrainingModel: NUSC>'])
        self.assertQuerysetEqual(multiplier_set, ['<TrainingMultiplier: warmup>'])
        self.assertEqual(multiplier.multiplier, '0.4')

    def test_create_training_edit_form(self):
        """
        The form can be used to edit the model.
        """
        self.client.login(username='user', password='password')
        team = test.create_team(user=self.user)
        response = self.client.post(reverse('teams:createTraining', kwargs={
                't_id': 0,
            }),
            {
                'team': team.id,
                'form-0-focus': 'warmup',
                'form-0-multiplier': '0.4',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'submit': 'Submit',
            },
            follow=True
        )
        training_model = TrainingModel.objects.all()
        multiplier_set = training_model[0].trainingmultiplier_set.all()
        multiplier = multiplier_set[0]
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(training_model, ['<TrainingModel: NUSC>'])
        self.assertQuerysetEqual(multiplier_set, ['<TrainingMultiplier: warmup>'])
        self.assertEqual(multiplier.multiplier, '0.4')

        response = self.client.post(reverse('teams:createTraining', kwargs={
                't_id': training_model[0].id,
            }),
            {
                'team': team.id,
                'form-0-focus': 'kick',
                'form-0-multiplier': 2,
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'submit': 'Submit',
            },
            follow=True
        )
        training_model = TrainingModel.objects.all()
        multiplier_set = training_model[0].trainingmultiplier_set.all()
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(training_model, ['<TrainingModel: NUSC>'])
        self.assertQuerysetEqual(multiplier_set, ['<TrainingMultiplier: kick>'])


# Show training

class TestShowTrainingView(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_show_training_page(self):
        """
        The training model form is displayed on the page (not hidden by a modal).
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        training_model = test.create_training_model(team)
        training_multiplier = test.create_training_multiplier(model=training_model)
        response = self.client.get(reverse('teams:showTraining'))
        self.assertContains(response, 'Training')
        self.assertContains(response, 'Northeastern University')
        self.assertContains(response, 'Warmup')


# Delete models

class TestDeleteModelsViews(TestCase):
    def setUp(self):
        self.user1 = test.create_user('user1', 'password')
        self.user2 = test.create_user('user2', 'password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

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

    def test_multiple_users_delete_team(self):
        """
        Deleting a team for one user should not delete it for another.
        """
        self.client.login(username='user1', password='password')
        team1 = test.create_team(user=self.user1)
        team2 = test.create_team(user=self.user2)
        response = self.client.get(reverse(
                'teams:deleteTeam',
                kwargs={'abbr': team1.abbr}),
            follow=True)
        self.assertQuerysetEqual(response.context['team_list'], [])

        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:teamList'))
        self.assertQuerysetEqual(
            response.context['team_list'],
            ['<Team: Northeastern University>'],
        )

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

    def test_multiple_users_delete_swimmer(self):
        """
        Deleting a team for one user should not delete it for another.
        """
        self.client.login(username='user1', password='password')
        team1 = test.create_team(user=self.user1)
        swimmer1 = test.create_swimmer(team=team1)
        team2 = test.create_team(user=self.user2)
        swimmer2 = test.create_swimmer(team=team2)
        response = self.client.get(reverse(
                'teams:deleteSwimmer',
                kwargs={'abbr': team1.abbr, 's_id': swimmer1.id}),
            follow=True)
        self.assertQuerysetEqual(response.context['swimmer_list'], [])

        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:swimmerList', kwargs={'abbr': team2.abbr}))
        self.assertQuerysetEqual(
            response.context['swimmer_list'],
            ['<Swimmer: Henry Gridley>'],
        )

    def test_delete_practice(self):
        """
        Deletes a practice.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team = test.create_team(user=self.user1)
        practice = test.create_practice(team=team, week=week)
        response = self.client.get(reverse(
                'teams:deletePractice',
                kwargs={'abbr': team.abbr, 'p_id': practice.id}),
            follow=True)
        self.assertEqual(response.context['practices'][0], ((None, (None, (None, (None, None)))), 'monday'))
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')

    def test_multiple_users_delete_practice(self):
        """
        Deleting a team for one user should not delete it for another.
        """
        self.client.login(username='user1', password='password')
        week = test.create_week()
        week.populate()
        team1 = test.create_team(user=self.user1)
        practice1 = test.create_practice(team=team1, week=week)
        team2 = test.create_team(user=self.user2)
        practice2 = test.create_practice(team=team2, week=week)
        response = self.client.get(reverse(
                'teams:deletePractice',
                kwargs={'abbr': team1.abbr, 'p_id': practice1.id}),
            follow=True)
        self.assertEqual(response.context['practices'][0], ((None, (None, (None, (None, None)))), 'monday'))

        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:practiceSchedule', kwargs={
                'abbr': team2.abbr,
                'w_id': week.id
            })
        )
        self.assertEqual(response.context['practices'][0][0][0].weekday, 'monday')
        self.assertContains(response, '7/10')
        self.assertContains(response, '7/16')

    def test_delete_training_model(self):
        """
        Deletes a training model.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        training_model = test.create_training_model(team)
        response = self.client.get(reverse('teams:deleteTraining', kwargs={
                't_id': training_model.id,
            }),
            follow=True,
        )
        self.assertEqual(response.context['teams'][0][1], None)

    def test_multiple_users_delete_training_model(self):
        """
        Deleting a training model for one user does not delete it for another.
        """
        self.client.login(username='user1', password='password')
        team1 = test.create_team(user=self.user1)
        training_model1 = test.create_training_model(team1)
        team2 = test.create_team(user=self.user2)
        training_model2 = test.create_training_model(team2)
        response = self.client.get(reverse('teams:deleteTraining', kwargs={
                't_id': training_model1.id,
            }),
            follow=True,
        )
        self.assertEqual(response.context['teams'][0][1], None)

        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('teams:showTraining'))
        self.assertEqual(response.context['teams'][0][1].team.name, 'Northeastern University')

    def test_delete_set(self):
        """
        Deletes a set.
        """
        self.client.login(username='user1', password='password')
        team = test.create_team(user=self.user1)
        week = test.create_week()
        week.populate()
        practice = test.create_practice(team, week)
        set1 = test.create_set(practice)
        rep1 = test.create_rep(set1)
        response = self.client.get(reverse('teams:deleteSet', kwargs={
                'abbr': team.abbr,
                'set_id': set1.id,
            }),
            follow=True,
        )
        self.assertQuerysetEqual(Set.objects.all(), [])
        self.assertQuerysetEqual(Rep.objects.all(), [])
        self.assertEqual(response.status_code, 200)
