from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth

class TestLogInView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(id=1, email='henry@example.com', username='henry', password='password')

    def tearDown(self):
        self.user.delete()

    def test_log_in_with_username(self):
        """
        A User can log in using their username and password.
        """
        response = self.client.post(reverse('accounts:login'),
            {'username': 'henry', 'password': 'password'}, follow=True)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teams/team_list.html')

    def test_log_in_with_email(self):
        """
        A User can log in using their email and password.
        """
        response = self.client.post(reverse('accounts:login'),
            {'username': 'henry@example.com', 'password': 'password'}, follow=True)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teams/team_list.html')

    def test_log_in_with_invalid_data(self):
        """
        A valid email/username and password are required to log in.
        """
        response = self.client.post(reverse('accounts:login'),
            {'username': 'dave', 'password': 'password'}, follow=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertTemplateNotUsed(response, 'teams/team_list.html')


class TestLogOutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(id=1, email='henry@example.com', username='henry', password='password')

    def tearDown(self):
        self.user.delete()

    def test_user_log_out(self):
        """
        The user is logged out.
        """
        response = self.client.get(reverse('accounts:logout'), follow=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/homepage.html')


class TestSignUpView(TestCase):
    def test_sign_up_with_valid_data(self):
        """
        A User signs in using their first name, last name, email, username,
        password, and password confirmation.
        """
        response = self.client.post(reverse('accounts:signup'),
            {
                'first_name': 'Henry',
                'last_name': 'Gridley',
                'email': 'henry@example.com',
                'username': 'henry',
                'password1': 'XAGEasdh!ad',
                'password2': 'XAGEasdh!ad',
            },
            follow=True)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teams/team_list.html')

    def test_sign_up_with_invalid_data(self):
        """
        A User will get an error if not all information is input.
        """
        response = self.client.post(reverse('accounts:signup'),
            {
                'email': 'henry@example.com',
                'username': 'henry',
                'password1': 'password',
            },
            follow=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
