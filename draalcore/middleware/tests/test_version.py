#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ApplicationVersionMiddleWare tests"""

# System imports
import logging
from django.http import HttpRequest, HttpResponse
from django.conf import settings

# Project imports
from draalcore.test_utils.basetest import BaseTestMiddleware
from ..version import ApplicationVersionMiddleware, VERSION_COOKIE_NAME


logger = logging.getLogger(__name__)


class ApplicationVersionTestCase(BaseTestMiddleware):
    """Application version middleware."""

    def get_response(self, request):
        self.responseFuncCalled += 1
        return HttpResponse()

    def test_request(self):
        """Version is validated."""

        obj = ApplicationVersionMiddleware(self.get_response)

        # GIVEN request has no application version cookie
        request = HttpRequest()

        # WHEN request is processed by the application version middleware
        resp = obj(request)

        # THEN error code should be returned
        self.assertEqual(resp.status_code, 418)

        self.clear_response()

        # ----------

        # GIVEN request has valid application version cookie
        request.COOKIES['app-version'] = settings.APP_VERSION

        # WHEN request is processed by the application version middleware
        response = obj(request)

        # THEN it should succeed
        self.assertTrue(response)
        self.assertEqual(self.responseFuncCalled, 1)

        # AND application version cookie should be present in the response
        self.assertTrue(VERSION_COOKIE_NAME in response.cookies)

        self.clear_response()
