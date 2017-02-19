#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
try:
    import httplib
except ImportError:
    import http.client as httplib
from mock import patch, MagicMock
from django.core.urlresolvers import reverse

from draalcore.test_utils.rest_api import GenericAPI
from draalcore.test_utils.basetest import BaseTestUser


class AuthGoogleTestCase(BaseTestUser):

    def test_google_sign_in(self):
        """Google sign-in URL is requested"""

        # GIVEN 3rd party authentication support in the system
        api = GenericAPI(self)

        # WHEN requesting Google sign-in URL
        response = api.auth_request('google')

        # THEN it should succeed
        self.assertEqual(response.status_code, httplib.FOUND)

        # AND URL is available
        location = response.header['Location']

        # AND it points to Google site
        self.assertTrue('https://accounts.google.com/o/oauth2/auth?' in location)

        # AND application specific state is present
        self.assertTrue('state' in location)

        # -----

        # WHEN local redirect page is present in URL request
        response = api.auth_request('google', {'next': '/main'})

        # THEN it should be present also in the Google URL
        location = response.header['Location']
        self.assertTrue('next' in location)

    def test_google_sign_in_callback_invalid_state(self):
        """OAuth2 callback with invalid state is called from Google sign-in"""

        # GIVEN callback URL for OAuth2 authentication
        api = GenericAPI(self)

        # WHEN URL is called without state parameter
        response = api.auth_callback('google')

        # THEN it should fail
        self.assertTrue(response.error)

    @patch('draalcore.auth.sites.google_oauth2.xsrfutil.validate_token')
    @patch('draalcore.auth.sites.google_oauth2.Base3rdPartyAuth.authenticate')
    @patch('draalcore.auth.sites.google_oauth2.build')
    @patch('draalcore.auth.sites.google_oauth2.FLOW.step2_exchange')
    def test_google_sign_in_callback(self, mock_flow_step2_exchange, mock_build, mock_auth, mock_token):
        """OAuth2 callback is called from Google sign-in"""

        mock_flow_step2_exchange.return_value = MagicMock()

        mock_build.return_value = MagicMock()
        mock_build.userinfo.return_value = MagicMock()
        mock_build.userinfo.get.return_value = MagicMock()
        mock_build.userinfo.get.execute = MagicMock()

        mock_auth.return_value = MagicMock()
        mock_token.return_value = True

        # GIVEN callback URL for OAuth2 authentication
        api = GenericAPI(self)

        # WHEN callback URL is called with valid data
        response = api.auth_callback('google', {
            'state': 'N-CPRCh_6kb5VJyGx7UdEDoxNDczNjk5ODkwnextL21haW4=',
            'client_id': 'client_id=abc.apps.googleusercontent.com',
            'code': '4/fumUC1u3N8kret1jp1lXqbbPTt1OxJz7i-N0Dg3yh68'
        })

        # THEN it should succeed
        self.assertEqual(response.status_code, httplib.FOUND)

        # AND redirect to correct page occurs
        self.assertEqual(response.header['Location'], '/main')


class TokenClient(object):
    def __init__(self, consumer, token):
        pass

    def request(self, url, method):
        content = 'oauth_token=abc&oauth_token_secret=secret'
        return dict(status='200'), content


class TokenClientFailure(TokenClient):
    def request(self, url, method):
        return dict(status='400'), None


class AuthTwitterTestCase(BaseTestUser):

    def initialize(self):
        self.api = GenericAPI(self)

    @patch('draalcore.auth.sites.twitter_oauth.client')
    def test_twitter_token_request(self, mock_client):
        """Request token retrieval from Twitter fails"""

        # GIVEN Twitter token request fails
        mock_client.request.return_value = (dict(status='400'), None)

        # WHEN requesting Twitter sign-in URL
        response = self.api.auth_request('twitter')

        # THEN it should succeed
        self.assertEqual(response.status_code, httplib.FOUND)

        # AND URL is available
        location = response.header['Location']

        # AND it points to local site
        self.assertEqual(reverse('auth-login'), location)

    @patch('draalcore.auth.sites.twitter_oauth.client')
    def test_twitter_sign_in_url(self, mock_client):
        """Twitter sign-in URL is requested"""

        # GIVEN Twitter request token
        content = 'oauth_token=abc'
        mock_client.request.return_value = (dict(status='200'), content)

        # WHEN requesting Twitter sign-in URL
        params = {'next': '/main'}
        response = self.api.auth_request('twitter', params)

        # THEN it should succeed
        self.assertEqual(response.status_code, httplib.FOUND)

        # AND URL is available
        location = response.header['Location']

        # AND it points to Twitter site
        self.assertTrue('https://api.twitter.com/oauth/authenticate?oauth_token=abc' in location)

        # AND callback URL is present
        self.assertTrue('oauth_callback=' in location)

        # AND redirect URL within callback URL is also present
        self.assertTrue('%3Fnext%3D%2Fmain' in location)

    def test_twitter_sign_in_callback_access_denied(self):
        """User denies application to use user's Twitter account"""

        # GIVEN user denies access from application to use user's account
        params = {
            'denied': 'adb'
        }

        # WHEN Twitter calls authentication callback
        response = self.api.auth_callback('twitter', params)

        # THEN user is redirected back to application login view
        self.assertEqual(response.header['Location'], reverse('auth-login'))

    def set_twitter_callback_params(self):
        session = self.client.session
        session['request_token'] = dict(oauth_token='12345', oauth_token_secret='abc')
        session.save()

        return {
            'oauth_verifier': 'aaBB'
        }

    @patch('draalcore.auth.sites.twitter_oauth.oauth.Client', side_effect=TokenClientFailure)
    def test_twitter_callback_authorized_token_access_failure(self, mock_client):
        """Callback URL fails to retrieve authorized token from Twitter"""

        # GIVEN Twitter callback URL with valid parameters
        params = self.set_twitter_callback_params()

        # WHEN requesting authorized token from Twitter
        response = self.api.auth_callback('twitter', params)

        # THEN user is redirected back to application login view
        self.assertEqual(response.header['Location'], reverse('auth-login'))

    @patch('draalcore.auth.sites.twitter_oauth.requests')
    @patch('draalcore.auth.sites.twitter_oauth.oauth.Client', side_effect=TokenClient)
    def test_twitter_callback_user_details_failure(self, mock_client, mock_requests):
        """Callback URL fails to retrieve user details from Twitter"""

        params = self.set_twitter_callback_params()

        # GIVEN retrieval of user details from Twitter fails
        mock_requests.get.return_value = MagicMock(status_code=404)

        # WHEN requesting user details from Twitter
        response = self.api.auth_callback('twitter', params)

        # THEN user is redirected back to application login view
        self.assertEqual(response.header['Location'], reverse('auth-login'))

    @patch('draalcore.auth.sites.twitter_oauth.requests')
    @patch('draalcore.auth.sites.twitter_oauth.oauth.Client', side_effect=TokenClient)
    def test_twitter_callback_success(self, mock_client, mock_requests):
        """Callback URL for Twitter login is called"""

        params = self.set_twitter_callback_params()

        # GIVEN retrieval of user details from Twitter
        mock_requests.codes = MagicMock(ok=200)
        resp = MagicMock(status_code=200)
        resp.json.return_value = dict(id='1234', name='test')
        mock_requests.get.return_value = resp

        # WHEN requesting user details from Twitter
        response = self.api.auth_callback('twitter', params)

        # THEN user is redirected back to application settings view
        self.assertEqual(response.header['Location'], reverse('settings-view'))


class TokenClientFb(object):
    def __init__(self, consumer):
        self.call_count = -1

    def request(self, url, method):
        self.call_count += 1

        if self.call_count == 0:
            content = 'access_token=adb'
            return dict(status='200'), content

        return dict(status='200'), json.dumps({
            'id': '123',
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@test.com'
        })


class TokenClientFbFailure(TokenClientFb):
    def request(self, url, method):
        return dict(status='400'), None


class AuthFacebookTestCase(BaseTestUser):

    def initialize(self):
        self.api = GenericAPI(self)

    def test_facebook_sign_in_url(self):
        """Facebook sign-in URL is requested"""

        # GIVEN Facebook authentication support

        # WHEN requesting Twitter sign-in URL
        response = self.api.auth_request('facebook')

        # THEN it should succeed
        self.assertEqual(response.status_code, httplib.FOUND)

        # AND URL is available
        location = response.header['Location']

        # AND it points to Twitter site
        self.assertTrue('https://www.facebook.com/dialog/oauth?client_id' in location)

        # AND callback URL is present
        self.assertTrue('redirect_uri=' in location)

    @patch('draalcore.auth.sites.fb_oauth.oauth.Client', side_effect=TokenClientFbFailure)
    def test_facebook_callback_authorized_token_access_failure(self, mock_client):
        """Callback URL fails to retrieve authorized token from Facebook"""

        # GIVEN retrieval of access token fails in callback URL

        # WHEN requesting authorized token from Facebook
        params = {'code': 'abc'}
        response = self.api.auth_callback('facebook', params)

        # THEN user is redirected back to application login view
        self.assertEqual(response.header['Location'], reverse('auth-login'))

    @patch('draalcore.auth.sites.fb_oauth.oauth.Client', side_effect=TokenClientFb)
    def test_facebook_callback_success(self, mock_client):
        """Callback URL for Facebook login is called"""

        # GIVEN retrieval of user details from Facebook succeeds

        # WHEN requesting user details from Facebook
        params = {'code': 'abc'}
        response = self.api.auth_callback('facebook', params)

        # THEN user is redirected back to application settings view
        self.assertEqual(response.header['Location'], reverse('main-view'))


class OneDriveClient(object):
    def __init__(self, url, auth_provider, http_provider):
        pass

    @property
    def auth_provider(self):
        return MagicMock(authenticate=MagicMock())


class OneDriveClientFailure(OneDriveClient):
    @property
    def auth_provider(self):
        auth = MagicMock(side_effect=Exception('Failure'))
        return MagicMock(authenticate=auth)


class DriveObject(object):
    def __init__(self):
        self._prop_dict = {
            'user': MagicMock(id=123, display_name='onedrive user')
        }

    @property
    def owner(self):
        return MagicMock(user=self._prop_dict['user'])


class DriveRequestBuilder(object):
    def __init__(self, url, client):
        pass

    def get(self):
        return DriveObject()


class DriveRequestBuilderFailure(DriveRequestBuilder):
    def get(self):
        raise Exception('Error')


class AuthOneDriveTestCase(BaseTestUser):

    def initialize(self):
        self.api = GenericAPI(self)

    def test_onedrive_sign_in_url(self):
        """OneDrive sign-in URL is requested"""

        # GIVEN OneDrive authentication support

        # WHEN requesting OneDrive sign-in URL
        response = self.api.auth_request('onedrive')

        # THEN it should succeed
        self.assertEqual(response.status_code, httplib.FOUND)

        # AND URL is available
        location = response.header['Location']

        # AND it points to OneDrive site
        self.assertTrue('https://login.live.com/oauth20_authorize.srf?' in location)
        self.assertTrue('scope=wl.signin+offline_access+onedrive.readonly' in location)

        # AND callback URL is present
        self.assertTrue('redirect_uri=' in location)

    def test_onedrive_callback_no_authorization_code(self):
        """No authorization code available in callback URL"""

        # GIVEN no authorization code available in callback URL

        # WHEN OneDrive calls the callback URL
        params = {}
        response = self.api.auth_callback('onedrive', params)

        # THEN user is redirected back to application login view
        self.assertEqual(response.header['Location'], reverse('auth-login'))

    @patch('draalcore.auth.sites.onedrive_oauth2.onedrivesdk.OneDriveClient', side_effect=OneDriveClientFailure)
    def test_onedrive_callback_authorization_code_redeem_failure(self, mock_client):
        """Failure to redeem authorization code for access code"""

        # GIVEN failure redeem authorization code for access code

        # WHEN making the request to redeem to code
        params = {'code': '123'}
        response = self.api.auth_callback('onedrive', params)

        # THEN user is redirected back to application login view
        self.assertEqual(response.header['Location'], reverse('auth-login'))

    @patch('draalcore.auth.sites.onedrive_oauth2.onedrivesdk.OneDriveClient', side_effect=OneDriveClient)
    @patch('draalcore.auth.sites.onedrive_oauth2.onedrivesdk.DriveRequestBuilder', side_effect=DriveRequestBuilderFailure)
    def test_onedrive_user_details_request_failure(self, mock_request, mock_client):
        """Failure to retrieve user details using Drive API"""

        # GIVEN failure to retrieve user details

        # WHEN retrieving user details via Drive API
        params = {'code': '123'}
        response = self.api.auth_callback('onedrive', params)

        # THEN user is redirected back to application login view
        self.assertEqual(response.header['Location'], reverse('auth-login'))

    @patch('draalcore.auth.sites.onedrive_oauth2.onedrivesdk.OneDriveClient', side_effect=OneDriveClient)
    @patch('draalcore.auth.sites.onedrive_oauth2.onedrivesdk.DriveRequestBuilder', side_effect=DriveRequestBuilder)
    def test_onedrive_auth_success(self, mock_request, mock_client):
        """User authenticates via Drive API"""

        # GIVEN OneDrive API for 3rd party authentication

        # WHEN authenticating via Drive API
        params = {'code': '123'}
        response = self.api.auth_callback('onedrive', params)

        # THEN is should succeed
        self.assertTrue(response.moved_temporarily)

        # AND user is redirected back to application settings view
        self.assertEqual(response.header['Location'], reverse('settings-view'))
