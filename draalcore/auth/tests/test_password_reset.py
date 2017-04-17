#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import patch, MagicMock
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from draalcore.test_utils.rest_api import AuthAPI
from draalcore.test_utils.basetest import BaseTest, create_user


class PasswordResetTestCase(BaseTest):

    def basetest_initialize(self):
        self.auth_api = AuthAPI(self)

        self.username = 'user2'
        self.password = 'user2-password'
        self.email = 'user2@gmail.com'
        self.user = create_user(self.username, self.password, self.email)

    @patch('draalcore.auth.authentication.actions.PasswordResetForm')
    def test_user_password_reset_request(self, pw_reset_form_mock):
        """User password reset is requested"""

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

    def test_user_password_reset_confirm_invalid_uidb64(self):
        """User password reset is confirmed with invalid uibd64"""

        # GIVEN invalid uidb and token data
        data = {
            'uidb64': 'abc',
            'token': 'aaa',
            'password': 'new-password'
        }

        # WHEN confirming password reset
        response = self.auth_api.password_reset_confirm(data)

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertEqual(response.data['errors'][0], u'Password reset unsuccessful')

    def test_user_password_reset_confirm_invalid_token(self):
        """User password reset is confirmed with invalid token"""

        # GIVEN invalid token data
        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)).decode('utf-8'),
            'token': 'aaa',
            'password': 'new-password'
        }

        # WHEN confirming password reset
        response = self.auth_api.password_reset_confirm(data)

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertEqual(response.data['errors'][0], u'Password reset unsuccessful')

    def test_user_password_reset_confirm(self):
        """User password reset is confirmed with valid data"""

        # GIVEN valid data
        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)).decode('utf-8'),
            'token': default_token_generator.make_token(self.user),
            'password': 'new-password'
        }

        # WHEN confirming password reset
        response = self.auth_api.password_reset_confirm(data)

        # THEN it should succeed
        self.assertTrue(response.success)
