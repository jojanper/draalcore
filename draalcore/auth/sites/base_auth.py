#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for 3rd party sign-in."""

# System imports
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# Project imports
from draalcore.exceptions import ExtAuthError

logger = logging.getLogger(__name__)


class Base3rdPartyAuth(object):
    PROVIDER = None
    BACKEND = None

    def get_callback_url(self):
        action = 'callback-{}'.format(self.PROVIDER)
        return '{}{}'.format(settings.EXT_AUTH_CALLBACK_URL, action)

    def get_redirect_url(self, request):
        return request.GET.get('next', '')

    def get_user(self, user_details):
        try:
            user = User.objects.get(username=user_details['username'])
            user.first_name = user_details['first_name']
            user.last_name = user_details['last_name']
            user.password = settings.SOCIAL_AUTH_USER_PASSWORD
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(username=user_details['username'],
                                            email=user_details['email'],
                                            password=settings.SOCIAL_AUTH_USER_PASSWORD,
                                            first_name=user_details['first_name'],
                                            last_name=user_details['last_name'])

        return user

    def authenticate(self, request, username, password=None):
        request.META['IS_SOCIAL'] = True
        user = authenticate(request, username=username, password=settings.SOCIAL_AUTH_USER_PASSWORD)
        login(request, user, backend=self.BACKEND)
        return user

    def login_failure(self):
        raise ExtAuthError('Login failed, please try again')
