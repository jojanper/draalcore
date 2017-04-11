#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Middleware for storing current user"""

from threading import local

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2014"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

_thread_locals = local()


def get_current_user():
    """Returns the current user, if exist, otherwise None"""
    return getattr(_thread_locals, "user", None)


def set_current_user(user):
    _thread_locals.user = user


def get_current_request():
    """Returns the HTTP request, if exist, otherwise None"""
    return getattr(_thread_locals, "request", None)


class CurrentUserMiddleware(object):
    def process_request(self, request):
        _thread_locals.user = request.user
        _thread_locals.request = request
