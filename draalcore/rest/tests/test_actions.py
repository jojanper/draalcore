#!/usr/bin/env python
# -*- coding: utf-8 -*-

from draalcore.test_utils.basetest import BaseTest
from draalcore.rest.actions import AbstractModelGetAction, AbstractModelItemGetAction


class ActionsTestCase(BaseTest):
    def test_model_get_action(self):
        """No execute method is defined for model GET action"""

        # GIVEN actions class without execute method implementation
        class TestGetAction(AbstractModelGetAction):
            pass

        # WHEN class is instantiated
        # THEN error should be raised
        self.assertRaises(TypeError, lambda: TestGetAction(None, None))

    def test_model_item_get_action(self):
        """No execute method is defined for model item GET action"""

        # GIVEN actions class without execute method implementation
        class TestItemGetAction(AbstractModelItemGetAction):
            pass

        # WHEN class is instantiated
        # THEN error should be raised
        self.assertRaises(TypeError, lambda: TestItemGetAction(None, None))
