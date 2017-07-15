from __future__ import unicode_literals
from unittest import skip, skipIf, skipUnless

from django.test import TestCase
from django.urls import reverse

from accounts.forms import LogInForm

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
