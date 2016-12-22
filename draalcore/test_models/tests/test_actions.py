#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model actions related tests"""

# System imports
import logging
import importlib
from mock import patch, PropertyMock

# Project imports
from ..models import TestModel
from ..actions import CreateNewAction
from .utils.mixins import TestModelMixin
from draalcore.test_utils.basetest import BaseTest, BaseTestUser


logger = logging.getLogger(__name__)


class CreateNewActionTestCase(BaseTest):
    """CreateNewAction action object"""

    def test_action_create(self):
        """Model action instance is create via create method"""

        # GIVEN action model

        # WHEN creating model instance via create method
        obj = CreateNewAction.create(None)

        # THEN instance should have correct model
        self.assertEqual(obj.model_cls, CreateNewAction.MODEL)


class ModelActionsTestCase(TestModelMixin, BaseTestUser):
    """Model actions."""

    def test_model_actions_listing(self):
        """Model actions are listed."""

        # GIVEN model
        model_name = self.model_name2

        # WHEN calling the actions listing
        response = self.api.model_actions(self.app_label, model_name)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct actions are returned
        self.assertEqual(response.data.keys(), ['create', 'create-new'])

        # AND action items return correct data fields
        for item in response.data:
            self.assertTrue('url' in response.data[item])
            self.assertTrue('display_name' in response.data[item])

        # ----------

        # WHEN retrieving all actions listing
        response = self.api.model_actions(self.app_label, model_name, {'actions': 'all'})

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct actions are returned
        self.assertEqual(response.data.keys(), ['create', 'create-new', 'get'])

        # ----------

        # GIVEN model ID
        data_id = self.obj2.id

        # WHEN calling the actions listing
        response = self.api.data_id_actions_listing(self.app_label, model_name, data_id)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct actions are returned
        self.assertEqual(response.data.keys(), ['edit', 'delete'])

        # AND action items return correct data fields
        for item in response.data:
            self.assertTrue('url' in response.data[item])
            self.assertTrue('display_name' in response.data[item])
            self.assertTrue('direct' in response.data[item])

        # ----------

        # WHEN retrieving all actions listing
        response = self.api.data_id_actions_listing(self.app_label, model_name, data_id, {'actions': 'all'})

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND correct actions are returned
        self.assertEqual(response.data.keys(), ['edit', 'get2', 'delete'])

    def test_model_invalid_action(self):
        """Invalid action is called via ReST API"""

        # GIVEN action that is not supported
        action = 'create2'

        # WHEN calling the action
        response = self.api.action(self.app_label, self.model_name2, action, {})

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertEqual(response.data['errors'][0], 'Action create2 not supported for method POST')

    @patch('draalcore.rest.actions.get_module')
    def test_model_no_actions_moduler(self, mock_module):
        """Model does not have actions module defined."""

        # GIVEN no actions module for the model
        mock_module.side_effect = ImportError()

        # WHEN calling the action with no data
        response = self.api.action(self.app_label, self.model_name2, 'create', {})

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertEqual(response.data['errors'][0], 'Following data fields are required: name, model1')

    @patch.object(importlib, 'import_module')
    def test_model_serializer_import_fail(self, mock_import):
        """Importing model serializer fails."""

        # GIVEN no actions module for the model
        mock_import.side_effect = ImportError()

        # WHEN calling the action with no data
        response = self.api.action(self.app_label, self.model_name2, 'create', {})

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertTrue('Unable to import serializer class for' in response.data['errors'][0])

    def test_model_edit_action_failure(self):
        """Edit action fails."""

        # GIVEN invalid model ID
        model_id = 0

        # WHEN calling the action
        response = self.api.model_action(self.app_label, self.model_name2, model_id, 'edit', {})

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertTrue('ID 0 does not exist' in response.data['errors'][0])

        # ----------

        # GIVEN valid model ID
        model_id = self.obj2.id

        # WHEN calling the action without editing data
        response = self.api.model_action(self.app_label, self.model_name2, model_id, 'edit', {})

        # THEN it should fail
        self.assertTrue(response.error)

    def test_model_edit_action(self):
        """Model is edited and then deleted."""

        # GIVEN editing data
        model_id = self.obj2.id
        obj = TestModel.objects.create(name='new value1')
        obj2 = TestModel.objects.create(name='new value2')
        data = {
            'name': 'edited value',
            'model1': obj.id,
            'model3': [obj.id, obj2.id],
            'duration': 123
        }

        # WHEN calling the action
        response = self.api.model_action(self.app_label, self.model_name2, model_id, 'edit', data)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND edited values should be present
        self.assertEqual(data['name'], response.data['name'])
        self.assertEqual(data['model1'], response.data['model1']['id'])
        self.assertEqual(len(data['model3']), len(response.data['model3']))
        self.assertEqual(data['model3'], [item.get('id', item) for item in response.data['model3']])

        # AND non-editable field remains unchanged
        self.assertTrue(response.data['duration'], -1)

        # ---------

        # GIVEN change in related item field
        data['model3'] = [obj.id]

        # WHEN calling the action
        response = self.api.model_action(self.app_label, self.model_name2, model_id, 'edit', data)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND edited values should be present
        self.assertEqual(data['name'], response.data['name'])
        self.assertEqual(data['model1'], response.data['model1']['id'])
        self.assertEqual(len(data['model3']), len(response.data['model3']))
        self.assertEqual(data['model3'], [item.get('id', item) for item in response.data['model3']])

        # ---------

        # GIVEN invalid editing data
        data['model3'] = [0]

        # WHEN calling the action
        response = self.api.model_action(self.app_label, self.model_name2, model_id, 'edit', data)

        # THEN it should fail
        self.assertTrue(response.error)

        # ----------

        # WHEN fetching model history
        response = self.api.history(self.app_label, self.model_name2, model_id)

        # THEN it should succeed
        self.assertTrue(response.success)
        self.assertEqual(len(response.data), 6)

        # ----------

        # WHEN deleting model item
        response = self.api.model_action(self.app_label, self.model_name2, model_id, 'delete')

        # THEN it should succeed
        self.assertTrue(response.success)

        # ----------

        # WHEN fetching model details for deleted item
        response = self.api.dataid(self.app_label, self.model_name2, model_id)

        # THEN it should fail
        self.assertTrue(response.error)
        self.assertEqual(response.data['errors'][0], 'ID 1 not found')

    def test_model_custom_action(self):
        """Custom create action is called."""

        # GIVEN custom create action
        action = 'create-new'

        # WHEN calling the action
        response = self.api.action(self.app_label, self.model_name2, action, {})

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND edited values should be present
        self.assertEqual({'data': 'abcd'}, response.data)

    def test_model_custom_get_action(self):
        """Model GET action is called."""

        # GIVEN custom get action
        action = 'get'

        # WHEN calling the action
        response = self.api.action(self.app_label, self.model_name2, action, method='get')

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND response should be valid
        self.assertEqual({'data': 'dcba'}, response.data)

    def test_model_item_custom_get_action(self):
        """Model item GET action is called."""

        # GIVEN custom get action for model item
        action = 'get2'
        model_id = self.obj2.id

        # WHEN calling the action
        response = self.api.model_action(self.app_label, self.model_name2, model_id, action, method='get')

        # THEN it should fail
        self.assertTrue(response.error)

        # AND response should have error message
        self.assertEqual(['error1', 'error2'], response.data['errors'])
