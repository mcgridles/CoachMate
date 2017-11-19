from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless

from django.test import TestCase
from django.urls import reverse

from accounts.forms import LogInForm, SignUpForm, SettingsForm

class TestLogInForm(TestCase):
    def test_log_in_form_valid_data(self):
        """
        LogInForm takes a username or email and password to validate.
        """
        form = LogInForm({
            'username': 'henry',
            'password': 'password',
        })
        self.assertTrue(form.is_valid())

    def test_log_in_form_invalid_data(self):
        """
        LogInForm will not validate without an email or username and password.
        """
        form = LogInForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'username': ['This field is required.'],
            'password': ['This field is required.'],
        })


class TestSignUpForm(TestCase):
    def test_sign_up_form_valid_data(self):
        """
        A first name, last name, email, username, password, and password
        confirmation are required for validation.
        """
        form = SignUpForm({
            'first_name': 'Henry',
            'last_name': 'Gridley',
            'email': 'henry@example.com',
            'username': 'henry',
            'password1': 'XAGEasdh!ad',
            'password2': 'XAGEasdh!ad',
        })
        self.assertTrue(form.is_valid())

    def test_sign_up_form_invalid_data(self):
        """
        A first name, last name, email, username, password, and password
        confirmation are required for validation.
        """
        form = SignUpForm({
            'email': 'henry@example.com',
            'username': 'henry',
            'password1': 'XAGEasdh!ad',
            'password2': 'XAGEasdh!ad',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'first_name': ['This field is required.'],
            'last_name': ['This field is required.'],
        })

    def test_sign_up_form_invalid_email(self):
        """
        User must enter a valid email address containing an '@'.
        """
        form = SignUpForm({
            'first_name': 'Henry',
            'last_name': 'Gridley',
            'email': 'example.com',
            'username': 'henry',
            'password1': 'XAGEasdh!ad',
            'password2': 'XAGEasdh!ad',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'email': ['Enter a valid email address.'],
        })


class TestSettingsForm(TestCase):
    def test_settings_form_valid_data(self):
        """
        Original password, a new password, and a matching password confirmation
        confirmation are required for validation.
        """
        form = SettingsForm({
            'old_passwd': 'test12345',
            'new_passwd1': 'XAGEasdh!ad',
            'new_passwd2': 'XAGEasdh!ad',
        })
        self.assertTrue(form.is_valid())

    def test_settings_form_invalid_data(self):
        """
        Original password, a new password, and a matching password confirmation
        confirmation are required for validation.
        """
        form = SettingsForm({
            'old_passwd': 'test12345',
            'new_passwd1': 'XAGEasdh!ad',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'new_passwd2': ['This field is required.'],
        })
