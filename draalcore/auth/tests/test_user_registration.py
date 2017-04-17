#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from mock import patch
from django.contrib.auth.models import User

from draalcore.test_utils.rest_api import AuthAPI
from draalcore.test_utils.basetest import BaseTest
from draalcore.auth.models import UserAccountProfile


class UserRegistrationTestCase(BaseTest):

    ERROR_TEXT = 'Following data items are missing: username, email, password, first_name, last_name'

    def basetest_initialize(self):
        self.auth_api = AuthAPI(self)

    def test_user_registration_no_parameters(self):
        """No user registration parameters are received"""

        # GIVEN no registration parameters
        data = {}

        # WHEN registering new user
        response = self.auth_api.register(data)

        # THEN it should fail
        self.assertTrue(response.error)

        # AND error message is available
        self.assertTrue('errors' in response.data)
        self.assertEqual(response.data['errors'][0], self.ERROR_TEXT)

    def test_user_registration_invalid_parameters(self):
        """Invalid user registration parameters are received"""

        err_text = 'Data field \'username\' must be of type string'

        # GIVEN invalid registration parameters
        data = {
            'username': 2,  # Number, should be string
            'password': 'password',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test'
        }

        # WHEN registering new user
        response = self.auth_api.register(data)

        # THEN it should fail
        self.assertTrue(response.error)

        # AND error message is available
        self.assertTrue('errors' in response.data)
        self.assertEqual(response.data['errors'][0], err_text)

    def _test_duplicate_username(self, username):
        """Username is already reserved for another user"""
        data = {
            'username': username,
            'password': 'password',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'user'
        }

        # WHEN registering new user
        response = self.auth_api.register(data)

        # THEN it should fail
        self.assertTrue(response.error)
        error_text = 'Username {} is already reserved, please select another name'.format(username)
        self.assertEqual(response.data['errors'][0], error_text)

    def _test_activate_user(self, activation_key):
        """User account is activated"""

        # GIVEN activation key for user
        data = {'activation_key': activation_key}
        accounts = UserAccountProfile.objects.all()
        self.assertFalse(accounts[0].user.is_active)

        # WHEN activating user
        response = self.auth_api.activate_user(data)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND user is activated
        accounts = UserAccountProfile.objects.all()
        self.assertTrue(accounts[0].user.is_active)

    def _test_activate_user2(self, activation_key):
        """Activated user account is activated again"""

        # GIVEN activation key for already activated user
        data = {'activation_key': activation_key}
        accounts = UserAccountProfile.objects.all()
        self.assertTrue(accounts[0].user.is_active)

        # WHEN activating user
        response = self.auth_api.activate_user(data)

        # THEN it should fail
        self.assertTrue(response.error)

        # AND error message is available
        self.assertEqual(response.data['errors'][0], 'Activation key not found')

    def _test_activate_user_key_expired(self, activation_key):
        """Activation key has expired"""

        # GIVEN user account is not activated within allowed time window
        user = User.objects.all()[0]
        expiration_date = datetime.timedelta(days=180)
        user.date_joined = user.date_joined - expiration_date
        user.save()

        # WHEN activating user account
        data = {'activation_key': activation_key}
        response = self.auth_api.activate_user(data)

        # THEN it should fail
        self.assertTrue(response.error)

        # AND error message is available
        self.assertEqual(response.data['errors'][0], 'Activation key expired')

        user.date_joined = user.date_joined + expiration_date
        user.save()

    def _test_activate_user_invalid_key(self):
        """User account is activated with invalid key"""

        # GIVEN user account is not activated within allowed time window
        data = {'activation_key': 'abcdefg'}

        # WHEN activating user account
        response = self.auth_api.activate_user(data)

        # THEN it should fail
        self.assertTrue(response.error)

        # AND error message is available
        self.assertEqual(response.data['errors'][0], 'Invalid activation key')

    @patch('draalcore.mailer.send_mail')
    def test_user_registration(self, mailer_mock):
        """User registration parameters are received"""

        mailer_mock.return_value = True

        # GIVEN registration parameters
        data = {
            'username': 'testuser',
            'password': 'password',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'user'
        }

        # WHEN registering new user
        response = self.auth_api.register(data)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND user account is available
        accounts = UserAccountProfile.objects.all()
        activation_key = accounts[0].activation_key
        self.assertEqual(accounts.count(), 1)
        self.assertEqual(accounts[0].user.username, data['username'])
        self.assertEqual(accounts[0].user.email, data['email'])

        # AND email is sent to user
        self.assertEqual(mailer_mock.call_count, 1)

        self._test_duplicate_username(data['username'])

        self._test_activate_user_invalid_key()
        self._test_activate_user_key_expired(activation_key)
        self._test_activate_user(activation_key)
        self._test_activate_user2(activation_key)
