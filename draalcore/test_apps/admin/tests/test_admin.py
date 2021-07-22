#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System imports
import logging

# Project imports
from draalcore.test_utils.basetest import BaseTestUser
from draalcore.test_apps.test_models.tests.utils.mixins import TestModelMixin


logger = logging.getLogger(__name__)


class AdminAppTestCase(TestModelMixin, BaseTestUser):
    """Admin app tests"""

    APP = 'admin'

    def test_unsupported_action(self):
        """Actions for unsupported applications are queried"""

        # GIVEN app that does not have application level actions
        app = 'dummy'

        # WHEN quering the aplication level actions
        response = self.api.app_actions(app)

        # THEN it should fail
        self.assertTrue(response.error)

    def test_admin_app_actions(self):
        """Admin app actions requiring user authentication are queried"""

        # GIVEN admin app
        # WHEN quering the application level actions
        response = self.api.app_actions(self.APP)

        # THEN it should succeed
        self.assertTrue(response.success)

        # -----

        for action, data in response.data.items():

            # WHEN calling available actions
            response = self.api.app_action(self.APP, action, data['method'], data=None)

            # THEN it should succeed
            self.assertTrue(response.success)

            # AND response data is available
            self.assertEqual(len(response.data), 1)

            # -----

            # WHEN calling action using HTTP method that is not supported
            response = self.api.app_action(self.APP, action, 'GET')

            # THEN it should fail
            self.assertTrue(response.error)

    def test_admin_app_public_actions(self):
        """Public admin actions are queried"""

        # GIVEN unauthenticated user
        self.logout()

        # WHEN quering the application level actions
        response = self.api.app_public_actions(self.APP)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND expected action data is received
        self.assertTrue('admin-public-action' in response.data)
        self.assertFalse(response.data['admin-public-action']['authenticate'], False)

    def test_admin_app_public_action(self):
        """Public admin action is executed"""

        # GIVEN unauthenticated user
        self.logout()

        # WHEN executing action
        kwargs = {'data': None}
        response = self.api.app_public_action(self.APP, 'admin-public-action', 'post', **kwargs)

        # THEN it should succeed
        self.assertTrue(response.success)

        # AND expected action data is received
        self.assertTrue('Ok' in response.data)
