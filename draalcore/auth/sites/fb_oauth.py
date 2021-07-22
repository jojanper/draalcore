#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Facebook OAuth interface."""

# System imports
import json
import logging
try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus

import oauth2 as oauth
from django.conf import settings

# Project imports
from .base_auth import Base3rdPartyAuth


logger = logging.getLogger(__name__)


FACEBOOK_REQUEST_TOKEN_URL = 'https://www.facebook.com/dialog/oauth'
FACEBOOK_ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
FACEBOOK_CHECK_AUTH = 'https://graph.facebook.com/me'


consumer = oauth.Consumer(key=settings.FACEBOOK_APP_ID, secret=settings.FACEBOOK_APP_SECRET)


class FacebookOAuth(Base3rdPartyAuth):
    PROVIDER = 'facebook'
    BACKEND = 'draalcore.auth.backend.FacebookOAuthBackend'

    def get_authorize_url(self, request):
        """Request and prepare URL for login using Facebook account."""
        base_url = '{}?client_id={}&redirect_uri={}&scope={}'
        return base_url.format(FACEBOOK_REQUEST_TOKEN_URL, settings.FACEBOOK_APP_ID,
                               quote_plus(self.get_callback_url()), 'email')

    def set_user(self, response):
        return self.get_user({
            'username': 'fb-{}'.format(response['id']),
            'email': response['email'],
            'first_name': response['first_name'],
            'last_name': response['last_name'],
        })

    def authorize(self, request):

        base_url = '{}?client_id={}&redirect_uri={}&client_secret={}&code={}'
        request_url = base_url.format(FACEBOOK_ACCESS_TOKEN_URL, settings.FACEBOOK_APP_ID,
                                      self.get_callback_url(), settings.FACEBOOK_APP_SECRET,
                                      request.GET.get('code'))

        # Get the access token from Facebook
        client = oauth.Client(consumer)
        response, content = client.request(request_url, 'GET')
        if response['status'] == '200':

            # Get profile info from Facebook
            base_url = '{}?access_token={}&fields=id,first_name,last_name,email'
            access_token = json.loads(content)['access_token']
            request_url = base_url.format(FACEBOOK_CHECK_AUTH, access_token)
            response, content = client.request(request_url, 'GET')
            if response['status'] == '200':
                user_data = json.loads(content)

                # Authenticate user
                logger.debug(user_data)
                user = self.set_user(user_data)
                return self.authenticate(request, user.username)

        self.login_failure()
