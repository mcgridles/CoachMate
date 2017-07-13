# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

class HomeViewTest(TestCase):
    def test_homepage(self):
        """
        Homepage contains pictures and info regarding features.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Learn More')
