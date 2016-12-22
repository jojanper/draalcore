#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base utility connection classes for testing."""

# System imports
import json
import httplib


class URLResponse(object):

    def __init__(self, response):
        self._response = response

    def __str__(self):
        return '%s(%s,%s,%s,%s)' % (self.__class__.__name__, self.status_code, self.data,
                                    self._response.context, self.header)

    @property
    def header(self):
        return self._response

    @property
    def status_code(self):
        return self._response.status_code

    @property
    def data(self):
        try:
            return json.loads(self._response.content)
        except ValueError:
            return self._response.content

    @property
    def content(self):
        return self._response.content

    @property
    def error(self):
        return self.status_code == httplib.BAD_REQUEST

    @property
    def forbidden(self):
        return self.status_code == httplib.FORBIDDEN

    @property
    def not_found(self):
        return self.status_code == httplib.NOT_FOUND

    @property
    def success(self):
        return self.status_code == httplib.OK

    @property
    def moved_temporarily(self):
        return self.status_code == httplib.FOUND

    @property
    def unauthorized(self):
        return self.status_code == httplib.UNAUTHORIZED

    @property
    def data_content(self):
        return self._response.get('Content-Disposition')

    @property
    def login_required(self):
        return True if '/login/?next=' in self.header['Location'] else False

    @property
    def www_authenticate_required(self):
        return ('WWW-Authenticate' in self.header) and self.unauthorized


class ClientConnectionUtility(object):

    CONTENT_TYPE_JSON = 'application/json'
    CONTENT_TYPE_X_WWW_FORM = 'application/x-www-form-urlencoded'
    CONTENT_TYPE_MULTIPART = 'multipart/form-data'

    def __init__(self, tester, kwargs=None):
        self._tester = tester
        self._kwargs = kwargs

    @property
    def client(self):
        return self._tester.client

    @property
    def tester(self):
        return self._tester

    def _response(self, response):
        return URLResponse(response)

    def _do_request(self, url, data, method, content_type, **kwargs):
        params = []
        if method != 'get':
            if content_type == self.CONTENT_TYPE_JSON:
                params = [json.dumps(data), self.CONTENT_TYPE_JSON]
            elif content_type == self.CONTENT_TYPE_X_WWW_FORM:
                params = [data]
            elif content_type == self.CONTENT_TYPE_MULTIPART:
                params = [data]

        response = getattr(self.client, method)(url, *params, **kwargs)
        return self._response(response)

    def get(self, url):
        return self._do_request(url, None, 'get', self.CONTENT_TYPE_JSON)

    def post(self, url, data, content_type='application/json', **kwargs):
        return self._do_request(url, data, 'post', content_type, **kwargs)

    def put(self, url, data):
        return self._do_request(url, data, 'put', self.CONTENT_TYPE_JSON)

    def patch(self, url, data):
        return self._do_request(url, data, 'patch', self.CONTENT_TYPE_JSON)

    def delete(self, url):
        return self._do_request(url, {}, 'delete', self.CONTENT_TYPE_JSON)

    def do_get(self, url):
        return self.get(url)

    def do_delete(self, url):
        return self.delete(url)

    def admin_listing(self, app, model):
        url = '/admin/%s/%s/' % (app, model)
        return self._do_request(url, None, 'get', 'text/html')

    def admin_details_for_model_id(self, app, model, model_id):
        url = '/admin/%s/%s/%s/change/' % (app, model, model_id)
        return self._do_request(url, None, 'get', 'text/html')

    def admin_history_for_model_id(self, app, model, model_id):
        url = '/admin/%s/%s/%s/history/' % (app, model, model_id)
        return self._do_request(url, None, 'get', 'text/html')

    def admin_change(self, app, model, model_id, data):
        url = '/admin/%s/%s/%s/change/' % (app, model, model_id)
        return self.post(url, data, content_type=self.CONTENT_TYPE_X_WWW_FORM)

    def admin_action(self, app, model, model_id, action):
        url = '/admin/%s/%s/' % (app, model)
        data = {
            u'action': action,
            u'select_across': 0,
            u'index': 0,
            u'_selected_action': model_id
        }
        return self.post(url, data, content_type=self.CONTENT_TYPE_X_WWW_FORM)
