#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Factory interface"""

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

# System imports
from abc import ABCMeta
from django.db.models.query import QuerySet

# Project imports
from draalcore.cache.cache import CacheBase


class QueryResult(object):
    """Encapsulates queryset or query object"""

    def __init__(self, query, cached=False, is_object=False):
        self._query = query
        self._cached = cached
        self._is_object = is_object

    @classmethod
    def create(cls, response):
        if isinstance(response, cls):
            return response

        is_object = not isinstance(response, QuerySet)
        return cls(response, is_object=is_object)

    @property
    def query(self):
        """Return queryset or object"""
        return self._query

    @property
    def cached(self):
        """Return True if result is cached version, False otherwise"""
        return self._cached is True

    @property
    def is_object(self):
        return self._is_object


class FactoryBase(CacheBase):
    """
    Base class for a factory. Factory is a collection of one or more
    model managers that comprise the required interface implementation.
    """

    __metaclass__ = ABCMeta

    manager = None

    def __init__(self, manager):
        super(FactoryBase, self).__init__()
        self.manager = manager

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.manager)

    def model_history(self, model_id):
        """Return the model events"""
        return QueryResult(self.manager.history(model_id=model_id))

    def do_query(self, req_obj):
        """
        Call either factory or manager method and return result
        as QueryResult object.
        """
        ref_obj = self.manager if not req_obj.is_factory else self
        response = getattr(ref_obj, req_obj.method)(*req_obj.args, **req_obj.kwargs)
        return QueryResult.create(response)


class Factory(FactoryBase):
    """Generic factory class"""
    pass
