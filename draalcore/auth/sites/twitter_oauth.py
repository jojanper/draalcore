#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Twitter OAuth interface."""

# System imports
import cgi
import logging
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
import oauth2 as oauth
from django.conf import settings
import requests
from requests_oauthlib import OAuth1
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

# Project imports
from .base_auth import Base3rdPartyAuth


logger = logging.getLogger(__name__)

consumer = oauth.Consumer(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
client = oauth.Client(consumer)

TWITTER_BASE_URL = 'https://api.twitter.com'
request_token_url = TWITTER_BASE_URL + '/oauth/request_token'
access_token_url = TWITTER_BASE_URL + '/oauth/access_token'
authenticate_url = TWITTER_BASE_URL + '/oauth/authenticate'
verify_credentials_url = TWITTER_BASE_URL + '/1.1/account/verify_credentials.json?include_email=true'


class TwitterOAuth(Base3rdPartyAuth):
    PROVIDER = 'twitter'

    def get_authorize_url(self, request):
        """Request and prepare URL for login using Twitter account."""

        # Redirect URL present?
        redirect_url = self.get_redirect_url(request)
        if redirect_url:
            redirect_url = '?next={}'.format(redirect_url)

        # Manually include the callback URL
        params = {'oauth_callback': '{}{}'.format(self.get_callback_url(), redirect_url)}

        # Get a request token from Twitter.
        params = urlencode(params)
        url = request_token_url + '?' + params
        resp, content = client.request(url, "GET")
        if resp['status'] != '200':
            return self.get_login_page()

        # Store the request token in a session for later use.
        request.session['request_token'] = dict(cgi.parse_qsl(content))

        # Redirect the user to the authentication URL on Twitter.
        return '{}?oauth_token={}&{}'.format(authenticate_url, request.session['request_token']['oauth_token'], params)

    def authorize(self, request):
        if 'denied' in request.GET:
            return HttpResponseRedirect(self.get_login_page())

        # Use the request token in the session to build a new client.
        token = oauth.Token(request.session['request_token']['oauth_token'],
                            request.session['request_token']['oauth_token_secret'])
        token.set_verifier(request.GET['oauth_verifier'])
        client2 = oauth.Client(consumer, token)

        # Request the authorized access token from Twitter.
        resp, content = client2.request(access_token_url, "GET")
        if resp['status'] != '200':
            return HttpResponseRedirect(self.get_login_page())

        # Get user details from Twitter
        access_token = dict(cgi.parse_qsl(content))
        auth = OAuth1(settings.TWITTER_TOKEN, settings.TWITTER_SECRET,
                      access_token['oauth_token'], access_token['oauth_token_secret'])
        response = requests.get(verify_credentials_url, auth=auth)
        if response.status_code != requests.codes.ok:
            return HttpResponseRedirect(self.get_login_page())

        # Authenticate user
        logger.debug(response.json())
        kwargs = {'twitter_response': response.json()}
        self.authenticate(request, **kwargs)

        # Redirect to settings view so that user can view user details and fill-in missing data
        return HttpResponseRedirect(reverse('settings-view'))
