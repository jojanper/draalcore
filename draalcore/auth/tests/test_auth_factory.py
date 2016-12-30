#!/usr/bin/env python
# -*- coding: utf-8 -*-

from draalcore.test_utils.basetest import BaseTest
from draalcore.auth.sites import AuthFactory


class AuthFactoryTestCase(BaseTest):

    def test_create(self):
        """Authentication instance is created"""

        obj = AuthFactory.create('google')
        self.assertTrue(obj is not None)
