#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Nginx + memcache middleware"""

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2014"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


AUTHENTICATED_ID = '1'
NON_AUTHENTICATED_ID = '2'


def page_version(request):
    try:
        user = getattr(request, 'user')
        version = AUTHENTICATED_ID if user.is_authenticated() else NON_AUTHENTICATED_ID
    except AttributeError:
        version = NON_AUTHENTICATED_ID

    return version


class NginxMemcachedCookieUpdate:
    """Middleware for setting up correct cookie for caching"""

    def process_response(self, request, response):
        try:
            version = page_version(request)
            response.set_cookie('pv', version)
        except AttributeError:
            pass

        return response
