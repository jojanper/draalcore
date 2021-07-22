#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpRequest

from draalcore.test_utils.basetest import BaseTest, create_user
from draalcore.auth.backend import GoogleOAuth2Backend, TwitterOAuthBackend, FacebookOAuthBackend, OneDriveOAuth2Backend


class BackendTestCaseMixin(object):

    def backend_validation(self, obj, ref_username):

        request = HttpRequest()
        request.META['IS_SOCIAL'] = True

        # GIVEN authentication response from remote site

        # WHEN user is authenticated
        user = obj.authenticate(request, username=ref_username)

        # THEN it should succeed
        self.assertEqual(user.username, ref_username)

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
        username = 'google-{}'.format(response['id'])
        create_user(username, 'testpassword', response['email'])
        self.backend_validation(GoogleOAuth2Backend(), username)


class TwitterOAuthBackendTestCase(BackendTestCaseMixin, BaseTest):

    def test_authentication(self):
        """Twitter OAuth signed-in user authenticates to application"""

        # User details from Twitter OAuth response
        response = {
            'id': '12345',
            'name': 'test',
            'email': 'test@case.com'
        }

        username = 'twitter-{}'.format(response['id'])
        create_user(username, 'testpassword', response['email'])
        self.backend_validation(TwitterOAuthBackend(), username)


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

        username = 'fb-{}'.format(response['id'])
        create_user(username, 'testpassword', response['email'])
        self.backend_validation(FacebookOAuthBackend(), username)


class OneDriveOAuth2BackendTestCase(BackendTestCaseMixin, BaseTest):

    def test_authentication(self):
        """OneDrive OAuth2 signed-in user authenticates to application"""

        # User details from OneDrive API
        response = {
            'id': '123456',
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@case.com'
        }

        username = 'od-{}'.format(response['id'])
        create_user(username, 'testpassword', response['email'])
        self.backend_validation(OneDriveOAuth2Backend(), username)
