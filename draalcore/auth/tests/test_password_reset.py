#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from mock import patch, MagicMock
from django.contrib.auth.models import User

from draalcore.test_utils.rest_api import AuthAPI
from draalcore.test_utils.basetest import BaseTestUser


class PasswordResetTestCase(BaseTestUser):

    def basetest_initialize(self):
        self.auth_api = AuthAPI(self)

    @patch('draalcore.auth.authentication.actions.PasswordResetForm')
    def test_user_password_reset(self, pw_reset_form_mock):
        """User password reset is requested"""

        self.logout()
        pw_reset_form = MagicMock()
        pw_reset_form.is_valid.return_value = True
        pw_reset_form.save = MagicMock()

        pw_reset_form_mock.return_value = pw_reset_form

        # GIVEN user email
        data = {'email': self.email}

        # WHEN requesting password reset
        response = self.auth_api.password_reset(data)

        # THEN it should succeed
        self.assertTrue(response.success)
        self.assertEqual(pw_reset_form_mock.call_count, 1)
