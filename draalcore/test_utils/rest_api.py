#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST API URL mapping utilities for unit testing."""

# System imports
import logging
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from django.urls import reverse

# Project imports
from draalcore.test_utils.connection import ClientConnectionUtility


logger = logging.getLogger(__name__)


class AuthAPI(ClientConnectionUtility):
    """Auth API for testing"""

    def _auth_url(self, name, base='rest-api-app-public-action'):
        return reverse(base, kwargs={'app': 'auth', 'action': name})

    def login(self, username, password):
        data = dict(username=username, password=password)
        return self.post(self._auth_url('login'), data)

    def token(self, username, password):
        data = dict(username=username, password=password)
        return self.post(self._auth_url('token'), data)

    def logout(self):
        return self.post(self._auth_url('logout'), {})

    def register(self, data):
        return getattr(self, 'post')(self._auth_url('register'), data)

    def activate_user(self, data):
        return getattr(self, 'post')(self._auth_url('activate'), data)

    def password_reset(self, data):
        return getattr(self, 'post')(self._auth_url('password-reset'), data)

    def password_reset_confirm(self, data):
        return getattr(self, 'post')(self._auth_url('password-reset-confirm'), data)

    def password_change(self, data):
        return getattr(self, 'post')(self._auth_url('password-change', base='rest-api-app-action'), data)

    def user_details(self):
        url = self._auth_url('auth-user-details', base='rest-api-app-action')
        return getattr(self, 'get')(url)


class FileUploadAPI(ClientConnectionUtility):
    """File upload API for testing"""

    def test_upload1(self, data, **kwargs):
        url = reverse('test-file-upload', kwargs={})
        return self.post(url, data, content_type=self.CONTENT_TYPE_MULTIPART, **kwargs)

    def test_upload2(self, data, **kwargs):
        url = reverse('test-file-upload2', kwargs={})
        return self.post(url, data, content_type=self.CONTENT_TYPE_MULTIPART, **kwargs)

    def test_upload3(self, data, **kwargs):
        url = reverse('test-file-upload3', kwargs={})
        return self.post(url, data, content_type=self.CONTENT_TYPE_MULTIPART, **kwargs)

    def file_upload(self, data, **kwargs):
        url = reverse('file-uploading', kwargs={})
        return self.post(url, data, content_type=self.CONTENT_TYPE_MULTIPART, **kwargs)


class HttpAPI(ClientConnectionUtility):
    """HTTP methods API for testing"""

    def invalid_http_method(self, method):
        kwargs = {}
        url = reverse('invalid-http-api', kwargs=kwargs)

        # No data present for HTTP GET and DELETE
        kwargs['data'] = {}
        if method in ['get', 'delete']:
            del kwargs['data']

        return getattr(self, method)(url, **kwargs)


class GenericAPI(ClientConnectionUtility):
    """Generic ReST API for testing"""

    def _dict2url(self, params):
        return '?' + urlencode(params) if params else ''

    def get_call(self, url, params={}):
        return getattr(self, 'get')(url + self._dict2url(params))

    def GET(self, app, model, params={}):
        url = reverse('rest-api-model', kwargs={'app': app, 'model': model})
        return getattr(self, 'get')(url + self._dict2url(params))

    def create(self, app, model, data):
        url = reverse('rest-api-model-action', kwargs={'app': app, 'model': model, 'action': 'create'})
        return getattr(self, 'post')(url, data)

    def model_action(self, app, model, model_id, action, data=None, method='post'):
        url = reverse('rest-api-model-id-action', kwargs={'app': app, 'model': model, 'id': model_id, 'action': action})
        return getattr(self, 'post')(url, data) if method == 'post' else getattr(self, 'get')(url)

    def action(self, app, model, action, data=None, method='post'):
        url = reverse('rest-api-model-action', kwargs={'app': app, 'model': model, 'action': action})
        return getattr(self, 'post')(url, data) if method == 'post' else getattr(self, 'get')(url)

    def model_actions(self, app, model, params=None):
        url = reverse('rest-api-model-actions-listing', kwargs={'app': app, 'model': model})
        return getattr(self, 'get')(url + self._dict2url(params))

    def data_id_actions_listing(self, app, model, model_id, params=None):
        url = reverse('rest-api-model-id-actions-listing', kwargs={'app': app, 'model': model, 'id': model_id})
        return getattr(self, 'get')(url + self._dict2url(params))

    def dataid(self, app, model, model_id, params=None):
        url = reverse('rest-api-model-id', kwargs={'app': app, 'model': model, 'id': model_id})
        return getattr(self, 'get')(url + self._dict2url(params))

    def history(self, app, model, model_id, params=None):
        url = reverse('rest-api-model-id-history', kwargs={'app': app, 'model': model, 'id': model_id})
        return getattr(self, 'get')(url + self._dict2url(params))

    def meta(self, app, model,  params=None):
        url = reverse('rest-api-model-meta', kwargs={'app': app, 'model': model})
        return getattr(self, 'get')(url + self._dict2url(params))

    def root_api(self, public=False):
        url = reverse('rest-api' if not public else 'rest-api-public')
        return getattr(self, 'get')(url)

    def app_actions(self, app):
        url = reverse('rest-api-app-actions-listing', kwargs={'app': app})
        return getattr(self, 'get')(url)

    def app_public_actions(self, app):
        url = reverse('rest-api-app-public-actions-listing', kwargs={'app': app})
        return getattr(self, 'get')(url)

    def app_action(self, app, action, method='get', **kwargs):
        url = reverse('rest-api-app-action', kwargs={'app': app, 'action': action})
        return getattr(self, method.lower())(url, **kwargs)

    def app_public_action(self, app, action, method='get', **kwargs):
        url = reverse('rest-api-app-public-action', kwargs={'app': app, 'action': action})
        return getattr(self, method.lower())(url, **kwargs)

    def auth_request(self, name, params=None):
        url = reverse('rest-api-app-public-action', kwargs={'app': 'auth', 'action': 'ext-auth-{}'.format(name)})
        return getattr(self, 'get')(url + self._dict2url(params))

    def auth_callback(self, name, params=None):
        url = reverse('rest-api-app-public-action', kwargs={'app': 'auth', 'action': 'callback-{}'.format(name)})
        return getattr(self, 'get')(url + self._dict2url(params))
