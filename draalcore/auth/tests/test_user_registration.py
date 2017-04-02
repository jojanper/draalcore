#!/usr/bin/env python
# -*- coding: utf-8 -*-

from draalcore.test_utils.rest_api import AuthAPI
from draalcore.test_utils.basetest import BaseTest


class UserRegistrationTestCase(BaseTest):
    def basetest_initialize(self):
        self.auth_api = AuthAPI(self)

    def test_user_registration_failure(self):
        """Invalid user account parameters are received"""

        # GIVEN no registration parameters
        # data = {}

        # WHEN registering new user
        # response = self.auth_api.register(data)

        # THEN it should fail
        # self.logging(response.status_code)
        # self.logging(response.content)
        # self.assertTrue(response.error)

        # AND error message is available
        # self.assertTrue('errors' in response.data)

        pass
