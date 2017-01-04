#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File upload tests"""

# System imports
import logging

# Project imports
from draalcore.test_utils.rest_api import FileUploadAPI
from draalcore.test_utils.basetest import BaseTestUser
from draalcore.test_utils.upload import upload_file


logger = logging.getLogger(__name__)


class FileUploadMixin(object):
    """File upload utility mixin"""

    def initialize(self):
        self.api = FileUploadAPI(self)

    def _upload_file(self, method='test_upload1', with_file=True, **kwargs):
        return upload_file(self.api, method, with_file, **kwargs)


class FileUploadTestCase(FileUploadMixin, BaseTestUser):
    """Test file upload API calls"""

    def test_file_upload_no_file(self):
        """No file attached when uploading file"""

        # GIVEN no file attachment
        with_file = False

        # WHEN user is uploading file
        response = self._upload_file(with_file=with_file)

        # THEN it should fail
        self.assertTrue(response.error)

    def test_file_upload_no_login(self):
        """User has not logged in to system when uploading file"""

        # GIVEN user that has not authenticated to system
        self.logout()

        # WHEN user is uploading file
        response = self._upload_file()

        # THEN it should fail
        self.assertTrue(response.www_authenticate_required)

    def test_file_upload(self):
        """User uploads file"""

        # GIVEN authenticated user

        # WHEN file is uploaded to valid API
        kwargs = {
            'HTTP_CONTENT_DISPOSITION': 'form-data; filename="{}"'.format('test_file')
        }
        response = self._upload_file(method='test_upload2', with_file=True, test_file='test1', **kwargs)

        # THEN it should succeed
        self.assertTrue(response.success)

    def test_file_upload_failure_no_upload_method_defined(self):
        """No upload method defined for upload API handler"""

        # GIVEN authenticated user

        # WHEN uploading file via API that does not implement upload method
        kwargs = {
            'HTTP_CONTENT_DISPOSITION': 'form-data; filename="{}"'.format('test_file')
        }
        response = self._upload_file(**kwargs)

        # THEN it should fail
        self.assertTrue(response.error)

    def test_file_upload_permission(self):
        """Custom permission required for uploading file"""

        # GIVEN unauthenticated user
        self.logout()

        # WHEN file is uploaded
        response = self._upload_file(method='test_upload3')

        # THEN it should fail
        self.assertTrue(response.www_authenticate_required)

        # ----------

        # WHEN authenticated user uploads file without upload permission
        self.login()
        response = self._upload_file(method='test_upload3')

        # THEN it should fail
        self.assertTrue(response.forbidden)
