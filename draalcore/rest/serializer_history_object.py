#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base serializer object class with event/history support"""

# System imports
import logging

# Project imports
from .req_query import QueryRequest
from draalcore.factory import Factory
from draalcore.rest.base_serializers import HistorySerializer
from draalcore.rest.serializer_object import SerializerDataItemObject, SerializerPaginatorMixin


logger = logging.getLogger(__name__)


class SerializerDataItemHistoryObject(SerializerPaginatorMixin, SerializerDataItemObject):
    """
    Base class for serializing model data item history. The class fetches history for model
    based on its ID.
    """

    has_history = True

    @classmethod
    def create(cls, request_obj, model_cls):
        obj = cls(request_obj)
        obj.factory = Factory(model_cls.objects)
        obj.serializer = HistorySerializer
        return obj

    def get_request_object(self):
        """Request queryset that returns the model changes/events"""
        return QueryRequest(method='model_history', is_factory=True,
                            query_kwargs={'model_id': self.data_id})
