#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Query specification for data serialization"""


class QueryRequest(object):
    """Encapsulate queryset specification"""

    def __init__(self, method, query_args=None, is_factory=False, query_kwargs=None):
        self._method = method
        self._query_args = query_args
        self._is_factory = is_factory
        self._query_kwargs = query_kwargs

    @property
    def method(self):
        return self._method

    @property
    def is_factory(self):
        return self._is_factory

    @property
    def args(self):
        if self._query_args and not isinstance(self._query_args, list):
            return [self._query_args]

        return self._query_args if self._query_args else []

    @property
    def kwargs(self):
        return self._query_kwargs if self._query_kwargs else {}
