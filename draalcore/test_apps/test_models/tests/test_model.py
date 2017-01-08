#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model related tests"""

# System imports
import logging
from django.db import models

# Project imports
from .utils.mixins import TestModelMixin
from ..models import TestModel, TestModel2
from draalcore.rest.model import ModelContainer
from draalcore.exceptions import ModelNotFoundError, ModelAccessDeniedError
from draalcore.test_utils.basetest import BaseTest, BaseTestUser
from draalcore.models.fields import AppModelCharField
from draalcore.test_apps.test_models.models import TestModelBaseModel


logger = logging.getLogger(__name__)
APP_LABEL = 'test_models'


class ModelContainerTestCase(BaseTest):
    """ModelContainer class tests"""

    def test_valid_model(self):
        """Model class is found"""
        model_cls = ModelContainer(APP_LABEL, TestModel2._meta.db_table).model_cls
        self.assertTrue(model_cls.__class__.__name__ is models.Model.__class__.__name__)

    def test_access_denied_model(self):
        """Access is denied to model class"""
        self.assertRaises(ModelAccessDeniedError, lambda: ModelContainer(APP_LABEL, TestModel._meta.db_table).model_cls)

    def test_invalid_model(self):
        """Model class is not found"""
        self.assertRaises(ModelNotFoundError, lambda: ModelContainer('web', 'model').model_cls)


class BaseModelTestCase(TestModelMixin, BaseTestUser):
    """Base model class"""

    def test_model_custom_field_editing_attribute_missing(self):
        """Custom field does not define editing attribute"""

        try:
            error = False

            # GIVEN invalid model field definition
            # WHEN model gets executed in the system
            class TestTestModel(models.Model):
                name = AppModelCharField(max_length=256, blank=True, null=True)

        except Exception as e:
            msg = e.args[0]
            error = True

        # THEN error should be raised
        self.assertTrue(error)

        # AND clear error description is present
        ref_msg = 'Field editing statuses are missing for AppModelCharField; called from TestTestModel'
        self.assertEqual(ref_msg, msg)

    def test_raw_sql(self):
        """Raw SQL query is performed"""

        # GIVEN raw SQL command
        sql = 'SELECT id, date_joined from auth_user WHERE id > %s;'
        params = ['0']

        # WHEN executing the SQL
        cursor = TestModel.execute_sql(sql, params)

        # THEN it should succeed
        results = cursor.fetchall()
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 2)

    def test_model_details_failure(self):
        """Model details call fails"""

        # GIVEN invalid model ID
        model_id = 300

        # WHEN model details are retrieved
        response = self.api.dataid(self.app_label, self.model_name2, model_id)

        # THEN it should fail
        self.assertTrue(response.error)

    def test_model_logger(self):
        """Model changes are saved"""

        # GIVEN model entry
        kwargs = {
            'name': 'test logging',
            'model1': self.obj1,
            'editing_user': self.user
        }

        # WHEN model is created
        obj = TestModel2.objects.create(**kwargs)
        obj.set_values(meta=self.obj1)

        # THEN model data should be visible from API
        response = self.api.dataid(self.app_label, self.model_name2, obj.id)
        self.assertTrue(response.success)

        # ----------

        # WHEN model details are retrieved
        response = self.api.dataid(self.app_label, self.model_name2, obj.id, params={
            'actions': 'all'
        })

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND details are present
        self.logging(response.data)
        self.assertEqual(len(response.data.keys()), 13)
        self.assertTrue('id' in response.data)
        self.assertTrue('name' in response.data)
        self.assertTrue('comments' in response.data)
        self.assertTrue('free_text' in response.data)
        self.assertTrue('model1' in response.data)
        self.assertTrue('model2' in response.data)
        self.assertTrue('model3' in response.data)
        self.assertTrue('modified_by' in response.data)
        self.assertTrue('last_modified' in response.data)
        self.assertTrue('type' in response.data)
        self.assertTrue('meta' in response.data)
        self.assertTrue('duration' in response.data)
        self.assertTrue('actions' in response.data)
        self.assertEqual(len(response.data['actions'].keys()), 3)
        self.assertTrue('edit' in response.data['actions'])
        self.assertTrue('get2' in response.data['actions'])
        self.assertTrue('delete' in response.data['actions'])

        # ----------

        # WHEN model details are retrieved for certain fields only
        response = self.api.dataid(self.app_label, self.model_name2, obj.id, {'fields': 'id'})

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND only required details are present
        self.assertTrue(len(response.data.keys()) == 1)
        self.assertTrue('id' in response.data)

        # ----------

        # WHEN model history is retrieved
        response = self.api.history(self.app_label, self.model_name2, obj.id)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND history details are present
        self.assertTrue(len(response.data) > 0)
        for history_data in response.data:
            self.assertTrue(len(history_data.keys()) == 3)
            self.assertTrue('events' in history_data)
            self.assertTrue(isinstance(history_data['events'], list))
            self.assertTrue('modified_by' in history_data)
            self.assertTrue('last_modified' in history_data)

        # ----------

        # WHEN model is edited
        edit_params = {
            'name': 'better name'
        }
        obj.set_values(**edit_params)

        response = self.api.history(self.app_label, self.model_name2, obj.id)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND history details are present
        self.assertEqual(len(response.data), 3)

    def test_model_activation(self):
        """Model item is deactivated and activated"""

        # GIVEN deactivated model item
        obj = self.obj2
        obj.deactivate()

        # WHEN retriving item details
        response = self.api.dataid(self.app_label, self.model_name2, obj.id)

        # THEN it should fail
        self.assertTrue(response.error)

        # -----

        # GIVEN model is activated
        obj.activate()

        # WHEN retriving item details
        response = self.api.dataid(self.app_label, self.model_name2, obj.id)

        # THEN it should succeed
        self.assertTrue(response.success)

    def test_basemodel_query(self):
        """Model is derived from BaseModel"""

        # GIVEN model that is derived from BaseModel (i.e., no status field present)
        model = TestModelBaseModel

        # WHEN retrieving model list
        items = model.objects.all()

        # THEN it should succeed
        self.assertEqual(len(items), 0)

    def test_public_manager_call(self):
        """Public manager method is called"""

        # GIVEN public access method to model's manager

        # WHEN fetching data listing using unsupported call method
        response = self.api.GET(self.app_label, self.model_name2, params={'call': 'call2'})

        # THEN it should fail
        self.assertTrue(response.error)

        # -----

        # WHEN fetching data listing using supported call method
        response = self.api.GET(self.app_label, self.model_name2, params={'call': 'call'})

        # THEN it should succeed
        self.assertTrue(response.success)

    def test_root_api(self):
        """Available applications and models for ReST API."""

        # GIVEN API

        # WHEN fetching available applications and models
        response = self.api.root_api()

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND it should have valid data
        for item in response.data:
            keys = item.keys()
            self.assertEqual(len(keys), 3)
            self.assertEqual(keys, ['model', 'actions', 'app_label'])

        # AND it contains also UI application models
        self.assertTrue(any('test' in d['app_label'] for d in response.data))

        # AND public applications are also available
        data = [item for item in response.data if item['app_label'] == 'admin']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['model'], None)
        self.assertEqual(len(data[0]['actions'].keys()), 1)

    def test_repr(self):
        """Test model objects must have printable representation"""
        self.assertTrue(repr(self.obj1))
        self.assertTrue(repr(self.obj2))
        self.assertTrue(repr(self.obj3))
        self.assertTrue(repr(self.obj4))
        self.assertTrue(repr(self.obj5))


class BaseModelMetaTestCase(TestModelMixin, BaseTestUser):

    def _validate_name(self, data):
        self.assertEqual(data, {
            "editable": True,
            "required": True,
            "type": "text",
            "help": "",
            "attributes": {
                "min_length": 0,
                "max_length": 256
            }
        })

    def _validate_model3(self, data):
        self.assertEqual(data, {
            "help": "",
            "attributes": {
                "model": "testmodel"
            },
            "type": "multiSelector",
            "required": False,
            "editable": True,
            "selector": {
                "url": "/api/system/test_models/testmodel",
                "displayKey": None
            }
        })

    def _validate_model2(self, data):
        self.assertEqual(data, {
            "help": "",
            "attributes": {
                "model": "testmodel"
            },
            "type": "selector",
            "required": False,
            "editable": True,
            "selector": {
                "url": "/api/system/test_models/testmodel",
                "displayKey": None
            }
        })

    def _validate_model1(self, data):
        self.assertEqual(data, {
            "help": "",
            "attributes": {
                "model": "testmodel"
            },
            "type": "selector",
            "required": True,
            "editable": True,
            "selector": {
                "url": "/api/system/test_models/testmodel",
                "displayKey": None
            }
        })

    def _validate_comments(self, data):
        self.assertEqual(data, {
            "editable": True,
            "required": False,
            "type": "text",
            "help": "",
            "attributes": {
                "min_length": 0,
                "max_length": 256
            }
        })

    def _validate_meta(self, data):
        self.assertEqual(data, {
            "$types": {
                "name": {
                    "editable": True,
                    "required": True,
                    "type": "text",
                    "help": "",
                    "attributes": {
                        "min_length": 0,
                        "max_length": 256
                    }
                }
            },
            "help": "Metadata information",
            "attributes": {
                "model": "testmodel"
            },
            "type": "object",
            "$order": [
                "name"
            ],
            "required": False,
            "editable": True,
            "label": "Meta data"
        })

    def _validate_freetext(self, data):
        self.assertEqual(data, {
            "editable": False,
            "required": False,
            "type": "textarea",
            "help": "",
            "attributes": {}
        })

    def test_model_meta_serialization(self):
        """Model meta serialization"""

        # GIVEN model in the system

        # WHEN fetching model meta
        response = self.api.meta(self.app_label, self.model_name2)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct number of items is returned
        self.assertEqual(len(response.data.keys()), 7)

        # AND meta data of items is correct
        self._validate_name(response.data['name'])
        self._validate_comments(response.data['comments'])
        self._validate_freetext(response.data['free_text'])
        self._validate_model1(response.data['model1'])
        self._validate_model2(response.data['model2'])
        self._validate_model3(response.data['model3'])
        self._validate_meta(response.data['meta'])
