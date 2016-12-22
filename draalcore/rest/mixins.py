#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mixins for ReST API processing"""


# Project imports
from .response_data import ResponseData


class GetMixin(object):
    def get(self, request, *args, **kwargs):
        return self._execute(request, *args, **kwargs)


class PostMixin(object):
    def post(self, request, *args, **kwargs):
        return self._execute(request, *args, **kwargs)


class PutMixin(object):
    def put(self, request, *args, **kwargs):
        return self._execute(request, *args, **kwargs)


class PatchMixin(object):
    def patch(self, request, *args, **kwargs):
        return self._execute(request, *args, **kwargs)


class DeleteMixin(object):
    def delete(self, request, *args, **kwargs):
        return self._execute(request, *args, **kwargs)


class FactoryDeleteMixin(DeleteMixin):
    def _delete(self, request_obj):
        fn = getattr(self.factory, 'call_' + request_obj.method)
        return ResponseData(fn(request_obj))
