#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Login middleware tests"""

# System imports
import logging
from mock import MagicMock, patch
from datetime import datetime, timedelta
from django.http import HttpRequest
from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse

# Project imports
from draalcore.test_utils.basetest import BaseTest
from ..login import LoginRequiredMiddleware, UserEmailRequiredMiddleware, AutoLogout, DateTimeSerializer


logger = logging.getLogger(__name__)


class LoginRequiredTestCase(BaseTest):
    """Login required middleware."""

    def test_request(self):
        """User authentication is validated."""

        obj = LoginRequiredMiddleware()

        # GIVEN request has no user authentication
        request = HttpRequest()
        request.path_info = '/view'
        request.user = MagicMock()
        request.user.is_authenticated = MagicMock(return_value=False)

        # WHEN request is processed by the login middleware
        response = obj.process_request(request)

        # THEN redirect response should returned
        self.assertIsNotNone(response)
        self.assertTrue('/login/?next=' in response['Location'])


class UserEmailRequiredTestCase(BaseTest):
    """User email required middleware."""

    def test_request_redirect(self):
        """Presence of user email is validated."""

        obj = UserEmailRequiredMiddleware()

        # GIVEN user data has no email included and user requests main page
        request = HttpRequest()
        request.path_info = '/'
        request.user = MagicMock(email='')
        request.user.is_authenticated = MagicMock(return_value=True)

        # WHEN request is processed by the middleware
        response = obj.process_request(request)

        # THEN redirect response should returned
        self.assertIsNotNone(response)
        self.assertTrue('{}?next='.format(reverse(settings.USER_EMAIL_REDIRECT)) in response['Location'])

        # -----

        # GIVEN user data has email included and user requests main page
        request = HttpRequest()
        request.path_info = '/'
        request.user = MagicMock(email='test@test.com')
        request.user.is_authenticated = MagicMock(return_value=True)

        # WHEN request is processed by the middleware
        response = obj.process_request(request)

        # THEN no response should be returned
        self.assertIsNone(response)


class AutoLogoutTestCase(BaseTest):
    """Auto logout middleware."""

    def test_request1(self):
        """User is not logged in."""

        obj = AutoLogout()

        # GIVEN unauthenticated user
        request = HttpRequest()
        request.user = MagicMock()
        request.user.is_authenticated = MagicMock(return_value=False)

        # WHEN request is processed by the auto logout middleware
        response = obj.process_request(request)

        # THEN it succeeds
        self.assertIsNone(response)

    @patch.object(auth, 'logout')
    def test_request2(self, logout):
        """User session has expired."""

        obj = AutoLogout()
        logout.return_value = True

        # GIVEN expired user session
        request = HttpRequest()
        request.user = MagicMock()
        request.user.is_authenticated = MagicMock(return_value=True)
        timestamp = datetime.now() - timedelta(0, settings.AUTO_LOGOUT_DELAY * 2, 0)
        request.session = {'last_touch': DateTimeSerializer(timestamp).encode}

        # WHEN request is processed by the auto logout middleware
        response = obj.process_request(request)

        # THEN redirect response is returned
        self.assertIsNotNone(response)
