#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Authentication backends."""

# System imports
from django.contrib.auth.models import User
from django.conf import settings

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


def get_user(user_details):
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


class BaseAuthBackend(object):
    """
    Base class for authentication.
    """

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class GoogleOAuth2Backend(BaseAuthBackend):
    """
    Authenticate user based on Google OAuth2 authentication information.
    """

    def authenticate(self, google_response):
        return get_user({
            'username': 'google-{}'.format(google_response['id']),
            'email': google_response['email'],
            'first_name': google_response['given_name'],
            'last_name': google_response['family_name'],
        })


class TwitterOAuthBackend(BaseAuthBackend):
    """
    Authenticate user based on Twitter authentication information.
    """

    def authenticate(self, twitter_response):
        return get_user({
            'username': 'twitter-{}'.format(twitter_response['id']),
            'email': '',
            'first_name': twitter_response['name'],
            'last_name': '',
        })


class FacebookOAuthBackend(BaseAuthBackend):
    """
    Authenticate user based on Facebook authentication information.
    """

    def authenticate(self, facebook_response):
        return get_user({
            'username': 'fb-{}'.format(facebook_response['id']),
            'email': facebook_response['email'],
            'first_name': facebook_response['first_name'],
            'last_name': facebook_response['last_name'],
        })


class OneDriveOAuth2Backend(BaseAuthBackend):
    """
    Authenticate user based on OneDrive authentication information.
    """

    def authenticate(self, onedrive_response):
        return get_user({
            'username': 'od-{}'.format(onedrive_response.user.id),
            'email': '',
            'first_name': onedrive_response.user.display_name,
            'last_name': '',
        })
