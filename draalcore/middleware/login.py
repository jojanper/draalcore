#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Login related middleware processors"""

# System imports
from re import compile
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib import auth

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

login_error_text = "The Login Required middleware requires authentication middleware " \
                   "to be installed. Edit your MIDDLEWARE_CLASSES settings to insert " \
                   "'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't " \
                   "work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes " \
                   "'django.template.context_processors.auth'."


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS.

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), login_error_text
        if not request.user.is_authenticated():
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(settings.LOGIN_URL + '?next=' + request.path)


class UserEmailRequiredMiddleware:
    """
    Middleware that requires a user to have email assigned. If email is not present, user is
    redirected to URL as indicated by settings.USER_EMAIL_REDIRECT.
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            if not request.user.email:
                path = request.path_info
                view_url = reverse(settings.USER_EMAIL_REDIRECT)
                if not path.startswith(view_url):
                    return HttpResponseRedirect(view_url + '?next=' + request.path)


class DateTimeSerializer(object):
    """Encode and decode datetime object"""

    def __init__(self, item):
        self._item = item

    @property
    def decode(self):
        """Decode string representation back to datetime object"""
        return datetime.strptime(self._item, '%Y-%m-%d %H:%M:%S.%f')

    @property
    def encode(self):
        """Return datetime as string representation"""
        return str(self._item)


class AutoLogout:
    """
    Middleware for logging out user if session has expired
    """
    def process_request(self, request):

        if not request.user.is_authenticated():
            # Can't log out if not logged in
            return

        try:
            cur_time = datetime.now()
            DELAY = settings.AUTO_LOGOUT_DELAY
            last_touch = DateTimeSerializer(request.session['last_touch']).decode
            if cur_time - last_touch > timedelta(0, DELAY, 0):
                auth.logout(request)
                del request.session['last_touch']
                return HttpResponseRedirect(settings.LOGIN_URL + '?next=' + request.path)
        except KeyError:
            pass

        request.session['last_touch'] = DateTimeSerializer(datetime.now()).encode

    @staticmethod
    def expires():
        return datetime.now() + timedelta(0, settings.AUTO_LOGOUT_DELAY, 0)
