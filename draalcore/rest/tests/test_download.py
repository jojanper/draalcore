#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from ..file_download import FileDownloader
from draalcore.test_utils.basetest import BaseTest
from draalcore.test_models.tests.test_upload import TEST_FILE_IMAGE


class FileDownloaderTestCase(BaseTest):
    def test_download_no_nginx(self):
        """Download is handled by application"""

        # GIVEN download file
        obj = FileDownloader.create(TEST_FILE_IMAGE, 'test')

        # WHEN requesting download
        response = obj.download()

        # THEN it should succeed
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename="test"')

    def test_download_nginx(self):
        """Download is handled by Nginx server"""

        # GIVEN application configuration where Nginx handles media downloads
        settings.PRODUCTION_ENVIRONMENT = True
        settings.X_ACCEL_REDIRECT = '/protected'

        # WHEN requesting download
        obj = FileDownloader.create(TEST_FILE_IMAGE, 'test')
        response = obj.download()

        # THEN HTTP header should indicate Nginx involvement
        self.assertEqual(response['X-Accel-Redirect'], '{}{}'.format(settings.X_ACCEL_REDIRECT, TEST_FILE_IMAGE))

        settings.PRODUCTION_ENVIRONMENT = False
        settings.X_ACCEL_REDIRECT = ''
