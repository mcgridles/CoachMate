from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

import teams.tests.test_setup as test

class TestGraphs(TestCase):
    def test_event_graph(self):
        pass
