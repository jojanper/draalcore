#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data serialization tests"""

# System imports
import os
import logging
from mock import MagicMock, patch, mock_open

# Project imports
from draalcore.rest.serializers import SerializerMixin
from draalcore.test_utils.basetest import BaseTest


class TestObject(object):
    def __init__(self, request_obj):
        self.request_obj = request_obj

    def serialize(self):
        self.called = True


class SerializerMixinTestCase(BaseTest):
    """SerializerMixin mixin."""

    def test_serializer_using_defined_object(self):
        """Serializer object is defined for handler."""

        request_obj = MagicMock()

        # GIVEN serializer handler with defined object
        class TestSerializer(SerializerMixin):
            serializer_obj = TestObject

        # WHEN request query is created
        obj = TestSerializer()
        ser_obj = obj._get_query(request_obj)

        # THEN is should succeed
        self.assertTrue(ser_obj.called)
