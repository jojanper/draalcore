#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HTTP request data class"""

import logging


logger = logging.getLogger(__name__)


class RequestData(object):
    """Request data container"""

    def __init__(self, request, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._request = request
        self._queryset = None

        try:
            self._data_params = request.DATA.copy() if hasattr(request, 'DATA') else request.data.copy()
        except AttributeError:
            self._data_params = {}

        try:
            self._url_params = request.GET.copy()
        except AttributeError:
            self._url_params = ''

    def __str__(self):
        return "%s(%s,%s,%s)" % (self.__class__.__name__,
                                 self._request,
                                 self._args,
                                 self._kwargs)

    @property
    def request(self):
        return self._request

    @property
    def user(self):
        return self.request.user

    @property
    def method(self):
        return self.request.method.lower()

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def data_params(self):
        return self._data_params

    @property
    def url_params(self):
        return self._url_params

    def has_url_param(self, key, value):
        if key in self.url_params:
            return self.url_params[key] == value

        return False

    def get_item(self, key):
        return self.data_params.get(key, None)

    def set_queryset(self, queryset):
        self._queryset = queryset

    @property
    def queryset(self):
        return self._queryset
