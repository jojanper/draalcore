#!/usr/bin/env python
# -*- coding: utf-8 -*-

from draalcore.test_utils.basetest import BaseTestUser


class AuthAPITestCase(BaseTestUser):
    def test_login_failure(self):
        """Invalid credentials are provided for sign-in"""

        # GIVEN sign-in API
        # WHEN user calls the API with invalid username
        response = self.auth_api.login('foo', self.password)

        # THEN it should fail
        self.assertTrue(response.error)

        # AND error message is available
        self.assertTrue('errors' in response.data)

    def test_login(self):
        """User does sign-in"""

        self.logout()

        # GIVEN sign-in API
        # WHEN user calls the API
        response = self.auth_api.login(self.username, self.password)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND user details are returned
        self.assertTrue('id' in response.data)
        self.assertTrue('display' in response.data)
        self.assertTrue('email' in response.data)
        self.assertTrue('expires' in response.data)
        self.assertTrue('token' in response.data)

    def test_logout(self):
        """User does sign-out"""

        # GIVEN sign-out API
        # WHEN user calls the API
        response = self.auth_api.logout()

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND access to authenticated APIs is denied
        response = self.api.root_api()
        self.assertTrue(response.moved_temporarily)

    def test_token(self):
        """User retrieves authentication token"""

        self.logout()

        # GIVEN token API
        api = self.auth_api

        # WHEN user calls the API with invalid credentials
        response = api.token(self.username, 'pw')

        # THEN it should fail
        self.assertTrue(response.error)

        # -----

        # WHEN user calls the API with valid credentials
        response = api.token(self.username, self.password)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND token is returned
        self.assertTrue('token' in response.data)
