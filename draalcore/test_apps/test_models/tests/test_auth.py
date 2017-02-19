#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Project imports
import base64
from rest_framework import HTTP_HEADER_ENCODING

# System imports
from .test_upload import FileUploadMixin
from draalcore.test_utils.basetest import BaseTestUser


class HttpAuthorizationTestCase(FileUploadMixin, BaseTestUser):
    """Test Basic auth over Rest API"""

    def _http_auth_call(self, auth_header):
        authorization = 'Basic {}'.format(auth_header)
        kwargs = {'HTTP_AUTHORIZATION': authorization}
        return self._upload_file(method='test_upload3', **kwargs)

    def test_http_authorization(self):
        """HTTP authorization over ReST API"""

        # GIVEN unauthenticated user
        self.logout()

        # WHEN file is uploaded
        response = self._upload_file(method='test_upload3')

        # THEN WWW-Authenticate header in response should be present
        self.assertTrue(response.www_authenticate_required)

        # ----------

        # WHEN incomplete authorization header is added to API call
        response = self._http_auth_call('')

        # THEN it should still fail
        self.assertTrue(response.unauthorized)
        self.assertTrue('detail' in response.data)

        # ----------

        # WHEN Authorization header is updated
        credentials = '%s:%s' % (self.username, self.password)
        auth_header = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode('utf-8')
        auth_header = '{}{}'.format(auth_header, ' invalid')
        response = self._http_auth_call(auth_header)

        # THEN it should still fail
        self.assertTrue(response.unauthorized)
        self.assertTrue('detail' in response.data)

        # ----------

        # WHEN Authorization header is not valid base64 encoded string
        credentials = '%s:%s' % (self.username, self.password)
        auth_header = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode('utf-8')
        auth_header = '{}{}'.format(auth_header, 'invalid')
        response = self._http_auth_call(auth_header)

        # THEN it should fail
        self.assertTrue(response.unauthorized)
        self.assertTrue('detail' in response.data)

        # ----------

        # WHEN Authorization header does not contain valid user credentials
        credentials = '%s:%s2' % (self.username, self.password)
        auth_header = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode('utf-8')
        response = self._http_auth_call(auth_header)

        # THEN it should fail
        self.assertTrue(response.unauthorized)
        self.assertTrue('detail' in response.data)

        # ----------

        # WHEN Authorization header is valid
        credentials = '%s:%s' % (self.username, self.password)
        auth_header = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode('utf-8')
        response = self._http_auth_call(auth_header)

        # THEN API call should fail due to missing permission
        self.assertTrue(response.forbidden)
