#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model admin related tests"""

# System imports
import logging

# Project imports
from .utils.mixins import TestModelMixin
from draalcore.test_utils.basetest import BaseTestUser


logger = logging.getLogger(__name__)


class BaseModelAdminTestCase(TestModelMixin, BaseTestUser):
    """Base model admin tests"""

    def initialize(self):
        super(BaseModelAdminTestCase, self).initialize()
        self.enable_superuser()

    def test_model_admin_listings(self):
        """Model listings via admin interface"""

        # GIVEN admin interface

        # WHEN listing model items
        response = self.api.admin_listing('admin', 'logentry')

        # THEN it should succeed
        self.assertTrue(response.success)

        # ----------

        # WHEN listing model item details
        response = self.api.admin_details_for_model_id(self.app_label, self.model_name2, self.obj2.id)

        # THEN it should succeed
        self.assertTrue(response.success)

        # ----------

        # WHEN viewing model item history
        response = self.api.admin_details_for_model_id('admin', 'logentry', self.obj2.id)

        # THEN it should succeed
        self.assertTrue(response.success)

    def test_model_event_not_json(self):
        """Model event is not json message"""

        # GIVEN admin changes model data
        data = {
            u'status': self.obj2.status,
            u'duration': 2,
            u'modified_by': 1,
            u'model1': 1,
            u'name': 'New name',
            u'_save': 'Save'
        }

        # WHEN save button is pressed
        response = self.api.admin_change(self.app_label, self.model_name2, self.obj2.id, data)

        # THEN it should succeed
        self.assertTrue(response.moved_temporarily)

        # ----------

        # WHEN fetching model's history
        response = self.api.history(self.app_label, self.model_name2, self.obj2.id)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND event message should be visible
        self.assertEqual(response.data[0]['events'], 'Changed name and duration.')

        # ----------

        # GIVEN admin sets model item to deleted status
        data = {
            u'status': self.obj2.STATUS_DELETED,
            u'modified_by': 1,
            u'model1': 1,
            u'name': 'New name',
            u'_save': 'Save'
        }
        response = self.api.admin_change(self.app_label, self.model_name2, self.obj2.id, data)
        self.assertTrue(response.moved_temporarily)

        # WHEN listing model items
        response = self.api.GET(self.app_label, self.model_name2)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND no data is returned
        self.assertEqual(len(response.data), 0)

        # ----------

        # GIVEN admin sets model item back to active status
        data = {
            u'status': self.obj2.STATUS_ACTIVE,
            u'modified_by': 1,
            u'model1': 1,
            u'name': 'New name',
            u'_save': 'Save'
        }
        response = self.api.admin_change(self.app_label, self.model_name2, self.obj2.id, data)
        self.assertTrue(response.moved_temporarily)

        # WHEN listing model items
        response = self.api.GET(self.app_label, self.model_name2)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND data is returned
        self.assertEqual(len(response.data), 1)
