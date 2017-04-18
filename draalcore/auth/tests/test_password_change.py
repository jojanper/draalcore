#!/usr/bin/env python
# -*- coding: utf-8 -*-

from draalcore.test_utils.rest_api import AuthAPI
from draalcore.test_utils.basetest import BaseTestUser


class PasswordChangeTestCase(BaseTestUser):

    def initialize(self):
        self.auth_api = AuthAPI(self)

    def test_user_password_change_invalid_old_password(self):
        """User password is invalid when requesting password change"""

        # GIVEN password change data
        data = {'old_password': 'abc', 'new_password1': 'pw', 'new_password2': 'pw'}

        # WHEN requesting password change
        response = self.auth_api.password_change(data)

        # THEN it should fail
        self.assertTrue(response.error)

    def test_user_password_change_mismatch_new_password2(self):
        """New passwords is not the same when requesting password change"""

        # GIVEN password change data
        data = {'old_password': self.password, 'new_password1': 'pw', 'new_password2': 'pw2'}

        # WHEN requesting password change
        response = self.auth_api.password_change(data)

        # THEN it should fail
        self.assertTrue(response.error)

    def test_user_password_change(self):
        """User password is changed"""

        # GIVEN password change data
        data = {'old_password': self.password, 'new_password1': 'pw', 'new_password2': 'pw'}

        # WHEN requesting password change
        response = self.auth_api.password_change(data)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND new password is ready for use
        self.logout()
        self.password = 'pw'
        self.assertTrue(self.login())
