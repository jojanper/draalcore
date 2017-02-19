#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model serializer object related tests"""

# System imports
import six
import logging
import importlib
from mock import patch, MagicMock

# Project imports
from ..models import TestModel2, TestModel5, TestModel6
from .utils.mixins import TestModelMixin
from draalcore.test_utils.basetest import BaseTestUser
from draalcore.rest.model import SerializerFinder
from draalcore.rest.serializer_object import SerializerDataObject


logger = logging.getLogger(__name__)


class ModelSerializerObjectTestCase(TestModelMixin, BaseTestUser):
    """Model has SERIALIZER_OBJECT attribute defined."""

    def initialize(self):
        super(ModelSerializerObjectTestCase, self).initialize()
        TestModel6.objects.create(name='test6')

    def test_object_loading(self):
        """Serializer object is loaded."""

        # GIVEN model class that has no serializer object attribute defined
        model_cls = TestModel2

        # WHEN retrieving model serializer object
        cls = SerializerFinder(model_cls).object

        # THEN no object is returned
        self.assertTrue(cls is None)

        # ----------

        # GIVEN model class that has serializer object attribute defined but not implemented
        model_cls = TestModel5

        # WHEN retrieving model serializer object
        cls = SerializerFinder(model_cls).object

        # THEN no object is returned
        self.assertTrue(cls is None)

        # ----------

        # GIVEN model class that has valid serializer object attribute defined
        model_cls = TestModel6

        # WHEN retrieving model serializer object
        cls = SerializerFinder(model_cls).object

        # THEN serializer object is returned
        self.assertTrue(cls is not None)

    @patch.object(importlib, 'import_module')
    def test_object_loading_import_error(self, import_module):
        """Import error occurs when serializer object is loaded."""

        # GIVEN import error occurs when importing serializer object for model class
        model_cls = TestModel6
        import_module.side_effect = ImportError()

        # WHEN retrieving model serializer object
        cls = SerializerFinder(model_cls).object

        # THEN no object is returned
        self.assertTrue(cls is None)

    def test_object_serializer(self):
        """Data is serialized through serializer object."""

        # GIVEN model class that has valid serializer object attribute
        params = {}
        model_name = TestModel6._meta.db_table

        # WHEN fetching listing data
        response = self.api.GET(self.app_label, model_name, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct data is returned
        self.assertEqual(len(response.data[0].keys()), 6)

        # ----------

        # GIVEN fields restriction for data listing
        params['fields'] = 'name,request_user'

        # WHEN fetching listing data
        response = self.api.GET(self.app_label, model_name, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct data is returned
        keys = [item for item in six.iterkeys(response.data[0])]
        self.assertEqual(len(keys), 2)
        self.assertEqual(set(keys), set(['request_user', 'name']))


class ModelSerializerDataObjectTestCase(TestModelMixin, BaseTestUser):
    """SerializerDataObject tests."""

    def initialize(self):
        super(ModelSerializerDataObjectTestCase, self).initialize()
        self.test_model_name = 'test6'
        TestModel6.objects.create(name=self.test_model_name)
        self.test_model_name2 = 'test62'
        TestModel6.objects.create(name=self.test_model_name2)

    def test_set_query(self):
        """Custom query is specified for serialization object"""
        request_obj = MagicMock(kwargs={})

        # GIVEN query is set for serializer
        obj = SerializerDataObject.create(request_obj, TestModel6)
        obj.set_query('test_model6', dict())

        # WHEN query data is serialized
        data = obj.serialize().data

        # THEN it should return all items
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], self.test_model_name)
        self.assertEqual(data[1]['name'], self.test_model_name2)
