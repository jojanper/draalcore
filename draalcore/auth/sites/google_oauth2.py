#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Google OAuth2 interface."""

# System imports
import base64
import httplib2
import logging
from django.conf import settings
from googleapiclient.discovery import build
from oauth2client.contrib import xsrfutil
from oauth2client.client import flow_from_clientsecrets

# Project imports
from .base_auth import Base3rdPartyAuth
from draalcore.exceptions import ExtAuthError


logger = logging.getLogger(__name__)


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = settings.GOOGLE_OAUTH2_CLIENT_SECRETS_FILE


FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    # Login scopes to be requested; basic profile information and user's Google account email address
    scope='profile email')


class GoogleOAuth2(Base3rdPartyAuth):
    """
    Google OAuth2 interface. The flow is as follows:
     - Prepare Google's login URL
     - Redirect to login URL that includes callback to this site
     - After successful login at Google's site, callback URL is called which then authenticates user to application

    See https://developers.google.com/api-client-library/python/guide/aaa_oauth
    """

    PROVIDER = 'google'

    def get_authorize_url(self, request):
        """Request and prepare URL for login using Google account."""

        # Redirect URL present?
        redirect_url = self.get_redirect_url(request)
        if redirect_url:
            redirect_url = '{}{}'.format('next', base64.encodestring(redirect_url.encode()))

        # Round-strip state for validating the callback message; it is a combination of secret token
        # and possible URL redirect value
        FLOW.params['state'] = '{}{}'.format(xsrfutil.generate_token(settings.SECRET_KEY, 1), redirect_url)
        FLOW.redirect_uri = self.get_callback_url()
        FLOW.params['prompt'] = 'consent'

        # And off to Google account login page
        return FLOW.step1_get_authorize_url()

    def authorize(self, request):
        """User successfully authenticated in Google's account site, now login the user locally."""

        state = str(request.GET.get('state'))
        split_state = state.split('next')
        base_state = split_state[0]

        # Make sure secret token is valid
        if not xsrfutil.validate_token(settings.SECRET_KEY, base_state, 1):
            raise ExtAuthError('Invalid state in OAuth2 callback')

        # Exchange authorization code for Credentials object
        credential = FLOW.step2_exchange(request.GET)
        http = credential.authorize(httplib2.Http())

        # Request basic profile information regarding the user
        # See https://developers.google.com/resources/api-libraries/documentation/oauth2/v2/python/latest/index.html
        # All available APIs are here: https://developers.google.com/api-client-library/python/apis/
        service = build("oauth2", "v2", http=http)
        user_info = service.userinfo().get().execute()
        logger.debug(user_info)

        # Done with credentials, revoke the token and make the credentials void as they are not needed anymore
        credential.revoke(httplib2.Http())

        # Authenticate the login user
        kwargs = {'google_response': user_info}
        return self.authenticate(request, **kwargs)
