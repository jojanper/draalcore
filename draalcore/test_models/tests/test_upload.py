#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File upload tests"""

# System imports
import os
import logging

# Project imports
from draalcore.test_utils.rest_api import FileUploadAPI
from draalcore.test_utils.basetest import BaseTestUser


logger = logging.getLogger(__name__)

TEST_FILE_IMAGE = os.path.join(os.path.dirname(__file__), 'pic.jpg')
TEST_FILE_CONTENT_HEADER = 'attachment; filename="pic.jpg"'
TEST_FILE_INVALID = os.path.join(os.path.dirname(__file__), 'test.invalid')
TEST_FILE_GIF = os.path.join(os.path.dirname(__file__), 'pic.gif')
TEST_FILE_MP3 = os.path.join(os.path.dirname(__file__), 'audio.mp3')
TEST_FILE_MP4 = os.path.join(os.path.dirname(__file__), 'video.mp4')


def upload_file(api, method='test_upload1', with_file=True, test_file='test1', **kwargs):
    if test_file == 'test1':
        upload_file = TEST_FILE_IMAGE
    elif test_file == 'test3':
        upload_file = TEST_FILE_GIF
    elif test_file == 'audio':
        upload_file = TEST_FILE_MP3
    elif test_file == 'video':
        upload_file = TEST_FILE_MP4
    else:
        upload_file = TEST_FILE_INVALID

    with open(upload_file) as fp:
        attachment = {"name": "test upload"}
        if with_file:
            attachment['file'] = fp

        return getattr(api, method)(attachment, **kwargs)


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
