from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth

class TestLogInView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(id=1, email='user@example.com', username='user', password='password')

    def tearDown(self):
        self.user.delete()

    def test_log_in_with_username(self):
        """
        A User can log in using their username and password.
        """
        response = self.client.post(reverse('accounts:login'),
            {'username': 'user', 'password': 'password'}, follow=True)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teams/team_list.html')

    def test_log_in_with_email(self):
        """
        A User can log in using their email and password.
        """
        response = self.client.post(reverse('accounts:login'),
            {'username': 'user@example.com', 'password': 'password'}, follow=True)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teams/team_list.html')

    def test_log_in_with_invalid_data(self):
        """
        A valid email/username and password are required to log in.
        """
        response = self.client.post(reverse('accounts:login'),
            {'username': 'not_a_user', 'password': 'password'}, follow=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertTemplateNotUsed(response, 'teams/team_list.html')


class TestLogOutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(id=1, email='user@example.com', username='user', password='password')

    def tearDown(self):
        self.user.delete()

    def test_user_log_out(self):
        """
        The user is logged out.
        """
        self.client.login(username='user', password='password')
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
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'username': 'jdoe',
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
                'email': 'john@example.com',
                'username': 'jdoe',
                'password1': 'password',
            },
            follow=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')


class TestSettingsView(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.user.set_password('test12345')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_settings_template(self):
        self.client.login(username='user', password='test12345')
        response = self.client.get(reverse('accounts:settings'))
        self.assertContains(response, 'Change Password')

    def test_settings_with_valid_data(self):
        """
        A User can change their password by inputting their old password, the new
        password, and retyping the new password to confirm.
        """
        self.client.login(username='user', password='test12345')
        response = self.client.post(reverse('accounts:settings'),
            {
                'old_passwd': 'test12345',
                'new_passwd1': 'XAGEasdh!ad',
                'new_passwd2': 'XAGEasdh!ad',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Success!')

    def test_settings_with_incorrect_password(self):
        """
        A User will get an error if the original password is not correct.
        """
        self.client.login(username='user', password='test12345')
        response = self.client.post(reverse('accounts:settings'),
            {
                'old_passwd': 'asdf',
                'new_passwd1': 'XAGEasdh!ad',
                'new_passwd2': 'XAGEasdh!ad',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect password')

    def test_settings_with_mismatched_new_passwords(self):
        """
        A User will get an error if the new password and the confirmation don't
        match.
        """
        self.client.login(username='user', password='test12345')
        response = self.client.post(reverse('accounts:settings'),
            {
                'old_passwd': 'test12345',
                'new_passwd1': 'XAGEasdh!ad',
                'new_passwd2': 'asdf',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match')
