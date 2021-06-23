#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Authentication backends."""

# System imports
import logging
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2016, 2021"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

logger = logging.getLogger(__name__)


class BaseAuthBackend(BaseBackend):
    """
    Base class for custom authentication.
    """

    def authenticate(self, request, username=None, password=None):
        # As Django goes through all authentication backends, limit backend usage
        # only to social authentication
        customBackend = request.META.get('IS_SOCIAL', False) if request else False
        if not customBackend:
            return None

        return User.objects.get(username=username)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class GoogleOAuth2Backend(BaseAuthBackend):
    """
    Authenticate user based on Google OAuth2 authentication information.
    """


class TwitterOAuthBackend(BaseAuthBackend):
    """
    Authenticate user based on Twitter authentication information.
    """


class FacebookOAuthBackend(BaseAuthBackend):
    """
    Authenticate user based on Facebook authentication information.
    """


class OneDriveOAuth2Backend(BaseAuthBackend):
    """
    Authenticate user based on OneDrive authentication information.
    """
