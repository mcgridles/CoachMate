from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
import os, shutil
from datetime import date, timedelta

from django.test import TestCase

from teams.TeamManager import TeamManager
from teams.models import Team, Event
import teams.tests.test_setup as test

class TestTeamManager(TestCase):
    def setUp(self):
        self.user = test.create_user(username='hgridley', password='password')
        self.team = test.create_team(self.user)
        self.swimmers = [
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

    def tearDown(self):
        self.user.delete()
        self.team.delete()

    def test_team_manager_init(self):
        """
        A TeamManager object takes a Team object and an optional zip file when
        initialized. A user directory should also be created in tmp/.
        """
        TeamManager(team=self.team)
        tm = TeamManager(team=self.team, zip_file='NUSC-NE-Roster003.zip')
        self.assertTrue(os.path.isdir(tm.user_folder_path))
        self.assertEqual(tm.team, self.team)
        self.assertEqual(tm.zip_file, 'NUSC-NE-Roster003.zip')

    def test_team_manager_load_roster_cl2(self):
        """
        Loads a team roster from the .CL2 file in the zip file.
        """
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/NUSC-NE-Roster003.zip', 'r') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_roster()
            self.assertEqual(msg[0], ('success', 'Roster imported'))

        new_swimmers = []
        for swimmer in self.team.swimmer_set.all():
            new_swimmers.append('<Swimmer: ' + swimmer.l_name + '>')
        self.assertEqual(new_swimmers, self.swimmers)

    def test_team_manager_load_roster_hy3(self):
        """
        Loads a team roster from the .HY3 file in the zip file.
        """
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/NUSC-NE-Roster004.zip', 'r') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_roster()
            self.assertEqual(msg[0], ('success', 'Roster imported'))

        new_swimmers = []
        for swimmer in self.team.swimmer_set.all():
            new_swimmers.append('<Swimmer: ' + swimmer.l_name + '>')
        self.assertEqual(new_swimmers, self.swimmers)

    def test_team_manager_load_invalid_zip_file(self):
        """
        An error message is displayed if the file is not named correctly.
        """
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/fftlighttest.zip') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_results()
            self.assertEqual(msg[0], ('error', 'Invalid file'))

    def test_team_manager_roster_upload_error(self):
        """
        An error message is displayed if swimmers can't be uploaded, or files can't
        be found.
        """
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/NUSC-NE-Roster003_bad.zip') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_roster()
            self.assertEqual(msg[0], ('error', 'Couldn\'t import swimmer(s)'))

        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/fftlighttest-Roster.zip') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_roster()
            self.assertEqual(msg[0], ('error', 'Couldn\'t find .CL2 or .HY3 file in zip file'))

    def test_team_manager_load_results(self):
        """
        Loads meet results from a .HY3 file in the zip file.
        """
        swimmer = test.create_swimmer(team=self.team)
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/RED-NE-Results005.zip', 'r') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_results()
            self.assertEqual(msg[0], ('success', 'Results imported'))

        events = Event.objects.filter(swimmer=swimmer)
        self.assertEqual(events[0].name, 'Henry Gridley')
        self.assertEqual(events[0].gender, 'M')
        self.assertEqual(events[0].team, self.team)
        self.assertEqual(events[0].event, '50 breast')
        self.assertEqual(events[0].time, timedelta(seconds=35.88))
        self.assertEqual(events[0].place, 7)
        self.assertEqual(events[0].date, date(2017,2,4))
        self.assertEqual(events[1].name, 'Henry Gridley')
        self.assertEqual(events[1].gender, 'M')
        self.assertEqual(events[1].team, self.team)
        self.assertEqual(events[1].event, '50 free')
        self.assertEqual(events[1].time, timedelta(seconds=23.34))
        self.assertEqual(events[1].place, 1)
        self.assertEqual(events[1].date, date(2017,2,4))

    def test_team_manager_results_upload_error(self):
        """
        An error message is displayed if results can't be uploaded, or files or
        the meet date can't be found.
        """
        swimmer1 = test.create_swimmer(team=self.team)
        swimmer2 = test.create_swimmer(team=self.team, first='David', last='Thornton')
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/RED-NE-Results005_bad_date.zip', 'r') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_results()
            self.assertEqual(msg[0], ('error', 'Couldn\'t find meet date'))

        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/RED-NE-Results005_bad_events.zip', 'r') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_results()
            self.assertEqual(msg[0], ('error', 'Couldn\'t import event for David Thornton'))
            self.assertEqual(msg[1], ('error', 'Couldn\'t import event for David Thornton'))
            self.assertEqual(msg[2], ('error', 'Couldn\'t import event for Henry Gridley'))

        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/fftlighttest-Results.zip') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_results()
            self.assertEqual(msg[0], ('error', 'Couldn\'t find .HY3 file in zip file'))

    def test_team_manager_load_roster_and_results(self):
        """
        Loads a team roster from a zip file then loads meet results for that team
        from a different zip file.
        """
        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/NUSC-NE-Roster003.zip', 'r') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_roster()
            self.assertEqual(msg[0], ('success', 'Roster imported'))

        with open('/Users/hgridley/Documents/Code/projects/CoachMate/teams/tests/test_files/RED-NE-Results005.zip', 'r') as f:
            tm = TeamManager(team=self.team, zip_file=f)
            msg = tm.load_results()
            self.assertEqual(msg[0], ('success', 'Results imported'))

        events = Event.objects.all()
        self.assertEqual(len(events), 113)
