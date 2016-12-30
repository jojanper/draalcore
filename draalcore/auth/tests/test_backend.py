#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import MagicMock
from django.contrib.auth.models import User

from draalcore.test_utils.basetest import BaseTest
from draalcore.auth.backend import GoogleOAuth2Backend, TwitterOAuthBackend, FacebookOAuthBackend, OneDriveOAuth2Backend


class BackendTestCaseMixin(object):

    def backend_test(self, obj, response, ref_username):

        count = User.objects.all().count()

        # GIVEN authentication response from remote site

        # WHEN user is authenticated
        user = obj.authenticate(response)

        # THEN it should succeed
        self.assertEqual(user.username, ref_username)

        # AND user is added to system
        self.assertEqual(count + 1, 1)

        # -----

        # WHEN user does another login
        user = obj.authenticate(response)

        # THEN it should succeed
        self.assertEqual(user.username, ref_username)

        # AND user count in the system remains the same
        self.assertEqual(count + 1, 1)

        # -----

        # WHEN get_user() method is called
        user = obj.get_user(user_id=user.id)

        # THEN it should return expected user
        self.assertEqual(user.username, ref_username)

        # -----

        # WHEN invalid user is provided to get_user method
        user = obj.get_user(user_id=0)

        # THEN no user should be returned
        self.assertEqual(user, None)


class GoogleOAuth2BackendTestCase(BackendTestCaseMixin, BaseTest):

    def test_authentication(self):
        """Google OAuth2 signed-in user authenticates to application"""

        # User details from Google OAuth2 API
        response = {
            'id': '12345',
            'given_name': 'test',
            'family_name': 'case',
            'email': 'test@case.com'
        }

        self.backend_test(GoogleOAuth2Backend(), response, 'google-{}'.format(response['id']))


class TwitterOAuthBackendTestCase(BackendTestCaseMixin, BaseTest):

    def test_authentication(self):
        """Twitter OAuth signed-in user authenticates to application"""

        # User details from Twitter OAuth response
        response = {
            'id': '12345',
            'name': 'test',
            'email': 'test@case.com'
        }

        self.backend_test(TwitterOAuthBackend(), response, 'twitter-{}'.format(response['id']))


class FacebookOAuthBackendTestCase(BackendTestCaseMixin, BaseTest):

    def test_authentication(self):
        """Facebook OAuth signed-in user authenticates to application"""

        # User details from Facebook OAuth response
        response = {
            'id': '12345',
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@case.com'
        }

        self.backend_test(FacebookOAuthBackend(), response, 'fb-{}'.format(response['id']))


class OneDriveOAuth2BackendTestCase(BackendTestCaseMixin, BaseTest):

    def test_authentication(self):
        """OneDrive OAuth2 signed-in user authenticates to application"""

        # User details from OneDrive API
        user = MagicMock(id=1, display_name="Test Test")
        response = MagicMock(user=user)

        self.backend_test(OneDriveOAuth2Backend(), response, 'od-{}'.format(user.id))
