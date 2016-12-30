#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OneDrive OAuth2 interface."""

# System imports
import logging
import onedrivesdk
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

# Project imports
from .base_auth import Base3rdPartyAuth


logger = logging.getLogger(__name__)


client_id = settings.ONEDRIVE_ID
client_secret = settings.ONEDRIVE_SECRET
api_base_url = 'https://api.onedrive.com/v1.0/'
scopes = ['wl.signin', 'offline_access', 'onedrive.readonly']


class OneDriveOAuth2(Base3rdPartyAuth):
    """
    OneDrive authentication and sign-in.

    See Python API in https://github.com/OneDrive/onedrive-sdk-python

    Authentication using code flow: https://github.com/OneDrive/onedrive-api-docs/blob/master/auth/msa_oauth.md
    """
    PROVIDER = 'onedrive'

    def get_authorize_url(self, request):
        """Request and prepare URL for login using OneDrive account."""
        http_provider = onedrivesdk.HttpProvider()
        auth_provider = onedrivesdk.AuthProvider(http_provider=http_provider, client_id=client_id, scopes=scopes)
        client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
        return client.auth_provider.get_auth_url(self.get_callback_url())

    def authorize(self, request):
        # Abort if no authorization code available
        code = request.GET.get('code', '')
        if not code:
            return HttpResponseRedirect(self.get_login_page())

        # Redeem the authorization code for access tokens
        try:
            http_provider = onedrivesdk.HttpProvider()
            auth_provider = onedrivesdk.AuthProvider(http_provider=http_provider, client_id=client_id, scopes=scopes)
            client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
            client.auth_provider.authenticate(code, self.get_callback_url(), client_secret)
        except Exception as e:
            logger.debug(e)
            return HttpResponseRedirect(self.get_login_page())

        # Get user details
        try:
            response = onedrivesdk.DriveRequestBuilder(api_base_url + 'drive', client).get()
        except Exception as e:
            logger.debug(e)
            return HttpResponseRedirect(self.get_login_page())

        # Authenticate user
        logger.debug(response._prop_dict)
        kwargs = {'onedrive_response': response.owner}
        self.authenticate(request, **kwargs)

        # Redirect to settings view so that user can view user details and fill-in missing data
        return HttpResponseRedirect(reverse('settings-view'))
