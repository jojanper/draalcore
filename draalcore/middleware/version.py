#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Application version middleware"""

# System imports
from django.http import HttpResponse
from django.conf import settings

# Project imports
from draalcore.middleware.base import BaseMiddleware

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015,2021"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


# Name of cookie that describes the version code
VERSION_COOKIE_NAME = getattr(settings, 'APP_VERSION_COOKIE_NAME', 'app-version')


class ApplicationVersionMiddleware(BaseMiddleware):
    """
    Middleware that checks the web clients requesting data from server are using compatible
    application code. If not, HTTP 418 status code is returned to indicate that the client code
    need to be reloaded before server is able to respond to any requests.
    """

    def process_request(self, request):
        # Application version in the request must match the current server version
        if request.COOKIES.get(VERSION_COOKIE_NAME) != settings.APP_VERSION:
            return HttpResponse('Application version mismatch. Please reload.', status=418)

    def process_response(self, request, response):
        # Always include the latest version in the response
        response.set_cookie(key=VERSION_COOKIE_NAME, value=settings.APP_VERSION)
        return response
