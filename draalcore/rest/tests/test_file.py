#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File uploading and downloading tests"""

# System imports
import os
import logging
import tempfile
import shutil
from mock import MagicMock, patch, mock_open
from django.core.files.uploadedfile import UploadedFile
from sys import version_info
try:
    import builtins  # pylint:disable=import-error
except ImportError:
    import __builtin__ as builtins  # pylint:disable=import-error

# Project imports
from ..file_upload import FileLoader
from draalcore.exceptions import AppException
from draalcore.test_utils.basetest import BaseTest
from draalcore.test_models.tests.test_upload import TEST_FILE_IMAGE


file_identifier = 'file'
logger = logging.getLogger(__name__)


def create_temporary_copy(path, name):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, name)
    shutil.copy2(path, temp_path)
    return temp_path


class FileLoaderTestCase(BaseTest):
    """FileLoader object."""

    def test_file_close_error(self):
        """Error is raised when Nginx upload file is closed."""

        # GIVEN error when closing upload file
        file_mock = MagicMock()
        file_mock.close = MagicMock(side_effect=OSError())

        # WHEN file upload request is processed
        post_data = {
            file_identifier + '.path': create_temporary_copy(TEST_FILE_IMAGE, 'test.nginx'),
            file_identifier + '.name': 'foo'
        }
        request = MagicMock(POST=post_data)

        open_mock = mock_open()
        with patch.object(builtins, "open", open_mock):
            open_mock.return_value = file_mock

            # THEN error is raised when file is closed
            obj = FileLoader(request, file_identifier).get_file()
            self.assertRaises(OSError, lambda: obj.close())

        os.remove(post_data[file_identifier + '.path'])

    def test_nginx_upload(self):
        """Nginx handles file upload."""

        # GIVEN Nginx handled file upload for the HTTP request
        post_data = {
            file_identifier + '.path': create_temporary_copy(TEST_FILE_IMAGE, 'test.nginx'),
            file_identifier + '.name': 'foo'
        }
        request = MagicMock(POST=post_data)

        # WHEN application loads the file from HTTP request
        obj = FileLoader(request, file_identifier).get_file()

        # THEN it should succeed
        self.assertTrue(isinstance(obj, UploadedFile))

        # AND file path corresponds to that set by Nginx server
        self.assertEqual(obj.temporary_file_path(), post_data.get(file_identifier + '.path'))

        # AND file name corresponds to that set by Nginx server
        self.assertEqual(obj.name, post_data.get(file_identifier + '.name'))

        # AND file can be closed
        self.assertEqual(obj.close(), None)

        os.remove(post_data[file_identifier + '.path'])

    def test_app_upload(self):
        """Application handles file upload."""

        # GIVEN file upload data in HTTP request
        file_data = {
            file_identifier: open(TEST_FILE_IMAGE, 'rb')
        }
        request = MagicMock(POST={}, FILES=file_data)

        # WHEN application loads the file from HTTP request
        obj = FileLoader(request, file_identifier).get_file()

        # THEN it should succeed
        self.assertTrue(isinstance(obj, UploadedFile))

        file_data[file_identifier].close()

    def test_upload_failure(self):
        """No files attached in upload"""
        # GIVEN HTTP request has no FILES
        request = MagicMock(POST={}, FILES=None)

        # WHEN application loads the file from HTTP request
        # THEN error should be raised
        self.assertRaises(AppException, lambda: FileLoader(request, file_identifier).get_file())

        # GIVEN HTTP request has no files attached
        request = MagicMock(POST={}, FILES={})

        # WHEN application loads the file from HTTP request
        # THEN error should be raised
        self.assertRaises(AppException, lambda: FileLoader(request, file_identifier).get_file())
