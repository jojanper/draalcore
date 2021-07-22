#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Authentication handlers for Django REST framework"""

# System imports
import base64
import binascii
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from rest_framework import authentication, exceptions, HTTP_HEADER_ENCODING


class SessionNoCSRFAuthentication(authentication.SessionAuthentication):
    """Session based authentication without CSRF validation"""
    def enforce_csrf(self, request):
        pass


class RestAuthentication(authentication.BaseAuthentication):
    """REST authentication against username+password."""

    www_authenticate_realm = 'User credentials'

    def authenticate(self, request):
        """
        Return user object if valid credentials (username + password) were provided,
        raise AuthenticationFailed exception otherwise.
        On success, user is also logged in.
        """
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            msg = 'Please provide authorization header'
            raise exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = 'Invalid basic header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid basic header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = 'Invalid basic header. Credentials not correctly base64 encoded'
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        return self._authenticate_credentials(request, userid, password)

    def _authenticate_credentials(self, request, userid, password):
        """
        Authenticate the userid and password against username and password.
        """
        auth_data = {'username': userid, 'password': password}
        f = AuthenticationForm(data=auth_data)

        # if authenticated log the user in.
        if f.is_valid():
            login(request._request, f.get_user())
            user = request._request.user
            if user.is_authenticated and user.is_active:
                return (request._request.user, None)

        raise exceptions.AuthenticationFailed('Invalid username or password')

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm
