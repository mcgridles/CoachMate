from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
import os, shutil

from django.test import TestCase

from teams.TeamManager import TeamManager
from teams.models import Team
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
            tm.load_roster()

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
            tm.load_roster()

        new_swimmers = []
        for swimmer in self.team.swimmer_set.all():
            new_swimmers.append('<Swimmer: ' + swimmer.l_name + '>')
        self.assertEqual(new_swimmers, self.swimmers)
