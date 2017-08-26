from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import teams.tests.test_setup as test
from teams.graphs import *

class TestGraphs(TestCase):
    def setUp(self):
        user = test.create_user('user', 'password')
        team = test.create_team(user)
        self.swimmer = test.create_swimmer(team)

    def tearDown(self):
        self.swimmer.delete()

    def test_event_graph(self):
        graph_event(self.swimmer)
