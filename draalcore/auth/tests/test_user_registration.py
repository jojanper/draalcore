#!/usr/bin/env python
# -*- coding: utf-8 -*-

from draalcore.test_utils.rest_api import AuthAPI
from draalcore.test_utils.basetest import BaseTest


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

    def test_user_registration(self):
        """User registration parameters are received"""

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