#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data serialization handler for ReST API"""

# System imports
import time
import logging

# Project imports
from .handlers import GetMixin, RestAPIBasicAuthView
from .response_data import ResponseData
from draalcore.rest.model import ModelContainer
from draalcore.rest.serializer_object import (SerializerDataObject, SerializerModelDataObject, SerializerDataItemObject,
                                              SerializerModelMetaObject)
from draalcore.rest.serializer_history_object import SerializerDataItemHistoryObject


logger = logging.getLogger(__name__)


class SerializerMixin(GetMixin):
    """
    ReST mixin to serialize model data. By default serializes data items from application model.
    """

    serializer_obj = None
    serializer_obj_cls = SerializerDataObject

    def _get_query(self, request_obj):
        """Return serializer object that contains the queryset"""

        # No serializer object predefined, construct it dynamically
        if self.serializer_obj is None:
            model_cls = ModelContainer(request_obj.kwargs['app'], request_obj.kwargs['model']).model_cls
            obj = self.serializer_obj_cls.create(request_obj, model_cls)
        else:
            obj = self.serializer_obj(request_obj)

        obj.serialize()
        return obj

    def _get(self, request_obj):
        """Get the queryset and return serialized data"""
        obj = self._get_query(request_obj)
        return ResponseData(obj.data if obj else '')


class SerializerModelMetaMixin(SerializerMixin):
    """ReST mixin to serialize model meta details"""
    serializer_obj_cls = SerializerModelMetaObject


class SerializerDataItemMixin(SerializerMixin):
    """ReST mixin to serialize model item details based on model ID"""
    serializer_obj_cls = SerializerDataItemObject


class SerializerDataItemHistoryMixin(SerializerDataItemMixin):
    """ReST mixin to serialize model item events/history based on model ID"""
    serializer_obj_cls = SerializerDataItemHistoryObject


class BaseSerializerHandler(SerializerMixin, RestAPIBasicAuthView):
    """ReST API handler for model data listings"""
    pass


class BaseSerializerModelMetaHandler(SerializerModelMetaMixin, BaseSerializerHandler):
    """ReST API handler for listing model meta data"""
    pass


class BaseSerializerDataItemHandler(SerializerDataItemMixin, BaseSerializerHandler):
    """ReST API handler for listing model item details"""
    pass


class BaseSerializerDataItemHistoryHandler(SerializerDataItemHistoryMixin, BaseSerializerDataItemHandler):
    """ReST API handler for listing model item event/history details"""
    pass
