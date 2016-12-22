#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ApplicationVersionMiddleWare tests"""

# System imports
import logging
from django.http import HttpRequest, HttpResponse
from django.conf import settings

# Project imports
from draalcore.test_utils.basetest import BaseTest
from ..version import ApplicationVersionMiddleware, VERSION_COOKIE_NAME


logger = logging.getLogger(__name__)


class ApplicationVersionTestCase(BaseTest):
    """Application version middleware."""

    def test_request(self):
        """Version is validated."""

        obj = ApplicationVersionMiddleware()

        # GIVEN request has no application version cookie
        request = HttpRequest()

        # WHEN request is processed by the application version middleware
        resp = obj.process_request(request)

        # THEN error code should be returned
        self.assertEqual(resp.status_code, 418)

        # ----------

        # GIVEN request has valid application version cookie
        request.COOKIES['app-version'] = settings.APP_VERSION

        # WHEN request is processed by the application version middleware
        resp = obj.process_request(request)

        # THEN it should succeed
        self.assertEqual(resp, None)

    def test_response(self):
        """Response contains application version."""

        obj = ApplicationVersionMiddleware()

        # GIVEN HTTP response
        response = HttpResponse()

        # WHEN response is processed by the application version middleware
        response = obj.process_response(None, response)

        # THEN application version cookie should be present
        self.assertTrue(VERSION_COOKIE_NAME in response.cookies)
