#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model data pagination and search tests"""

# System imports
import logging
from mock import patch, PropertyMock

# Project imports
from ..models import TestModel2
from .utils.mixins import TestModelMixin
from draalcore.test_utils.basetest import BaseTestUser


logger = logging.getLogger(__name__)


class ModelPaginationTestCase(TestModelMixin, BaseTestUser):
    """Model listing is paginated"""

    def initialize(self):
        super(ModelPaginationTestCase, self).initialize()
        TestModel2.objects.create(name='test2', model1=self.obj1)
        TestModel2.objects.create(name='test3', model1=self.obj1)

    def test_model_dt_pagination(self):
        """Model listing is paginated using DataTables format"""

        # GIVEN items for models

        # WHEN paginating listing data
        params = {'draw': 0, 'start': 0, 'length': 1, 'fields': 'id'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND output format should match the required plugin format
        self.assertTrue('aaData' in response.data)
        self.assertTrue('draw' in response.data)
        self.assertTrue('recordsTotal' in response.data)
        self.assertTrue('recordsFiltered' in response.data)
        self.assertEqual(response.data['recordsTotal'], 3)
        self.assertEqual(response.data['recordsFiltered'], 3)

        # AND first item is returned
        self.assertEqual(len(response.data['aaData']), 1)
        self.assertEqual(response.data['aaData'][0]['id'], 1)

        # ----------

        # WHEN fetching second page
        params = {'draw': 1, 'start': 1, 'length': 1, 'fields': 'id'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND second item is returned
        self.assertEqual(len(response.data['aaData']), 1)
        self.assertEqual(response.data['aaData'][0]['id'], 2)

        # ----------

        # WHEN invalid pagination range is specified
        params = {'draw': 5, 'start': 10, 'length': 2, 'fields': 'id'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND no items are returned
        self.assertEqual(len(response.data['aaData']), 0)

    def test_model_simple_pagination(self):
        """Model listing is paginated using simple format"""

        # GIVEN items for models

        # WHEN paginating listing data
        params = {'start': 0, 'length': 2, 'fields': 'id'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND required data items are returned
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], 1)
        self.assertEqual(response.data[1]['id'], 2)

    def test_model_invalid_pagination(self):
        """Invalid pagination parameters are specified"""

        # GIVEN items for models

        # WHEN invalid pagination parameters are specified
        params = {'start': 0, 'length': 'length', 'fields': 'id'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND all items are returned
        self.assertEqual(len(response.data), 3)

        # ----------

        # WHEN invalid pagination range is specified
        params = {'start': 10, 'length': 2, 'fields': 'id'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND no items are returned
        self.assertEqual(len(response.data), 0)

    def test_model_dt_pagination_failure(self):
        """Pagination fails due to paging error"""

        # GIVEN failure in pagination
        cls_prop = 'draalcore.rest.serializer_object.SerializerPaginatorMixin._page_number'
        with patch(cls_prop, new_callable=PropertyMock) as mock_page:
            mock_page.return_value = 'as'

            # WHEN paginating listing data
            params = {'draw': 1, 'start': 1, 'length': 1, 'fields': 'id'}
            response = self.api.GET(self.app_label, self.model_name2, params)

            # THEN it should succeed
            self.assertTrue(response.success)

            # AND first item is returned
            self.assertEqual(len(response.data['aaData']), 1)
            self.assertEqual(response.data['aaData'][0]['id'], 1)


class ModelSearchPaginationTestCase(TestModelMixin, BaseTestUser):
    """Model listing is searched and paginated"""

    def initialize(self):
        super(ModelSearchPaginationTestCase, self).initialize()
        TestModel2.objects.create(name='test2', model1=self.obj1)
        TestModel2.objects.create(name='test3', model1=self.obj1)
        TestModel2.objects.create(name='demo1', model1=self.obj1)

    def test_model_dt_search(self):
        """API listing items are searched"""

        # GIVEN items for models

        # WHEN searching items
        params = {'draw': 0, 'start': 0, 'length': 20, 'fields': 'id', 'search[value]': 'e'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND output format should match the required plugin format
        self.assertTrue('aaData' in response.data)
        self.assertTrue('draw' in response.data)
        self.assertTrue('recordsTotal' in response.data)
        self.assertTrue('recordsFiltered' in response.data)
        self.assertEqual(response.data['recordsTotal'], 4)
        self.assertEqual(response.data['recordsFiltered'], 4)

        # ----------

        # WHEN searching items and ordering based on descending ID
        params = {'draw': 0, 'start': 0, 'length': 1, 'fields': 'id,name', 'search[value]': 'test',
                  'order[0][column]': 0, 'columns[0][data]': 'id', 'order[0][dir]': 'desc'}
        response = self.api.GET(self.app_label, self.model_name2, params)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct result is returned
        self.assertEqual(len(response.data['aaData']), 1)
        self.assertEqual(response.data['aaData'][0]['id'], 3)
        self.assertEqual(response.data['aaData'][0]['name'], 'test3')
        self.assertEqual(response.data['recordsTotal'], 4)
        self.assertEqual(response.data['recordsFiltered'], 3)
