#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General ReST API related tests"""

# System imports
from mock import MagicMock

# Project imports
from ..models import TestModel
from .utils.rest_api import HttpAPI
from .utils.mixins import TestModelMixin
from draalcore.rest.request_data import RequestData
from draalcore.rest.response_data import ResponseData
from draalcore.test_utils.basetest import BaseTestUser
from draalcore.rest.mixins import FactoryDeleteMixin


class ResponseDataTestCase(BaseTestUser):
    """Test ResponseData class"""

    def test_response_data_repr(self):
        """ResponseData has readable representation of the object."""

        # GIVEN ResponseData instance
        obj = ResponseData(data=12, message='Test')

        # WHEN obtaining readable representation of the object
        txt = str(obj)

        # THEN it should succeed
        self.assertTrue(len(txt) > 0)


class RequestDataTestCase(BaseTestUser):
    """Test RequestData class"""

    def initialize(self):
        self.request = MagicMock(GET={}, method='GET', DATA={'test': 'new'})

    def test_request_data_repr(self):
        """RequestData has readable representation of the object."""

        # GIVEN RequestData instance
        obj = RequestData(request=self.request)

        # WHEN obtaining readable representation of the object
        txt = str(obj)

        # THEN it should succeed
        self.assertTrue(len(txt) > 0)

    def test_request_data_method(self):
        """Has method property"""
        self.assertEqual(RequestData(request=self.request).method, self.request.method.lower())

    def test_request_data_args(self):
        """Has args property"""
        args = ['22', 3]
        self.assertEqual([arg for arg in RequestData(self.request, *args).args], args)

    def test_request_data_get_item(self):
        """Has get_item method"""
        self.assertEqual(RequestData(request=self.request).get_item('test'), 'new')


class FactoryDeleteMixinTestCase(BaseTestUser):
    """Test FactoryDeleteMixin."""

    def test_factory_delete_mixin(self):
        """HTTP DELETE through factory calls delete method."""

        # GIVEN FactoryDeleteMixin instance
        obj = FactoryDeleteMixin()
        obj.factory = MagicMock()
        obj.factory.call_delete.return_value = 'working'
        request_obj = MagicMock(method='delete')

        # WHEN calling the delete method
        response = obj._delete(request_obj)

        # THEN it should succeed
        self.assertEqual(response.data, 'working')


class APITestCase(BaseTestUser):
    """Test HTTP GET, PUT, POST, PATCH and DELETE ReST API calls"""

    def initialize(self):
        self.api = HttpAPI(self)

    def test_http_method_not_implemented(self):
        """API handler is not configured correctly"""

        # GIVEN HTTP methods
        for method in ['get', 'put', 'post', 'patch', 'delete']:

            # WHEN HTTP call is made to API that is invalid
            response = self.api.invalid_http_method(method)

            # THEN it should fail
            self.assertTrue(response.error)
            self.assertTrue('errors' in response.data)


class HttpGetModelTestCase(TestModelMixin, BaseTestUser):
    """Generic ReST API is called with HTTP GET"""

    def test_model_not_available(self):
        """Model data is not available for external API fetching"""

        # GIVEN app and model name

        # WHEN fetching data for the model via generic ReST API
        response = self.api.GET(self.app_label, self.model_name)

        # THEN it should fail as access is denied
        self.assertTrue(response.error)
        self.assertTrue('errors' in response.data)
        self.assertTrue('not allowed' in response.data['errors'][0])

    def test_model_listing(self):
        """Model data listing is fetched"""

        # GIVEN app and model name

        # WHEN fetching data for the model via generic ReST API
        response = self.api.GET(self.app_label, self.model_name2, {'fields': 'id'})

        # THEN it should succeed
        self.assertTrue(response.success)

    def test_model_serializer_missing(self):
        """Serializer not defined for model"""

        # GIVEN app and model name

        # WHEN fetching data for the model via generic ReST API
        response = self.api.GET(self.app_label, self.model_name3)

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertTrue('No data serializer' in response.data['errors'][0])

    def test_model_serializer_not_found(self):
        """Serializer not found for model"""

        # GIVEN app and model name

        # WHEN fetching data for the model via generic ReST API
        response = self.api.GET(self.app_label, self.model_name4)

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertTrue('Invalid data serializer' in response.data['errors'][0])

    def test_model_string_representation(self):
        """Model should have textual representation"""
        self.assertTrue(str(self.obj1))
        self.assertTrue(str(self.obj2))
        self.assertTrue(str(self.obj3))
        self.assertTrue(str(self.obj4))


class HttpPostModelTestCase(TestModelMixin, BaseTestUser):
    """Generic ReST API is called with HTTP POST"""

    def test_model_post_not_allowed(self):
        """Model data is not available for external API editing"""

        # GIVEN app and model name

        # WHEN creating new data item
        data = {}
        response = self.api.create(self.app_label, self.model_name, data)

        # THEN it should fail
        self.assertTrue(response.error)

    def test_model_item_creation(self):
        """New item is created via ReST API"""

        # GIVEN ReST API parameters for creating new item
        params = [
            # model that is not supported by the API
            (self.model_name3, {}, 'error'),

            # model that is supported by the API
            (self.model_name2, {}, 'error'),  # No parameters

            # invalid post data
            (self.model_name2, {
                'name': 'test test',
                'comments': 'ok',
                'model1': 'abc'  # String is not allowed
            }, 'error'),

            # invalid post data
            (self.model_name2, {
                'name': 'test test',
                'comments': 'ok',
                'model1': 0  # 0 is not valid ID
            }, 'error'),

            # invalid post data
            (self.model_name2, {
                'name': 'test test',
                'comments': 'ok',
                'model1': None  # None is not allowed
            }, 'error'),

            # valid post data
            (self.model_name2, {
                'name': 'test test',
                'comments': 'ok',
                'model1': 1,
                'model2': None,
                'model3': None
            }, 'success'),

            # invalid post data
            (self.model_name2, {
                'name': 'test test',
                'comments': 'ok',
                'model1': 1,
                'model2': None,
                'model3': ['asa']  # Invalid, must be list of integers
            }, 'error'),

            # valid post data
            (self.model_name2, {
                'name': 'test test',
                'comments': 'ok',
                'model1': 1,
                'model2': None,
                'model3': [self.obj1.id]
            }, 'success')
        ]

        # WHEN creating the item
        for param in params:
            response = self.api.create(self.app_label, param[0], param[1])

            # THEN it should return expected response
            self.assertTrue(getattr(response, param[2]))

            # AND proper response data should be present
            if param[2] is 'success':
                self.assertEqual(len(response.data.keys()), 13)

    def test_model_item_many2many_creation(self):
        """New item is created via ReST API with many-2-many fields"""

        obj = TestModel.objects.create(name='test33')

        # GIVEN input with many-2-many field data
        params = {
            'name': 'test test m2m',
            'comments': 'ok',
            'free_comment': None,
            'model1': 1,
            'model2': None,
            'model3': [self.obj1.id, obj.id]
        }

        # WHEN creating the item
        response = self.api.create(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND many-2-many field items should be present
        self.assertEqual(len(response.data['model3']), 2)
