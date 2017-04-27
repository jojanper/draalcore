#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for 3rd party sign-in."""

# System imports
from django.conf import settings
from django.contrib.auth import authenticate, login

# Project imports
from draalcore.exceptions import ExtAuthError


class Base3rdPartyAuth(object):
    PROVIDER = None

    def get_callback_url(self):
        action = 'callback-{}'.format(self.PROVIDER)
        return '{}{}'.format(settings.EXT_AUTH_CALLBACK_URL, action)

    def get_redirect_url(self, request):
        return request.GET.get('next', '')

    def authenticate(self, request, **kwargs):
        user = authenticate(**kwargs)
        login(request, user)
        return user

    def login_failure(self):
        raise ExtAuthError('Login failed, please try again')
