# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.user.set_password('password')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_homepage(self):
        """
        Homepage contains pictures and info regarding features.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Learn more')

    def test_homepage_redirect(self):
        """
        if a user is logged in they should be redirected to their teams page
        when going to the homepage.
        """
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertTemplateUsed(response, 'teams/team_list.html')
