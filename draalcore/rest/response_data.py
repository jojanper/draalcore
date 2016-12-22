#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Response data object"""


class ResponseData(object):
    """Generic response data container"""

    def __init__(self, data='', message=''):
        self._data = data
        self._message = message

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, self._data, self._message)

    @property
    def data(self):
        return self._data

    @property
    def message(self):
        return self._message
