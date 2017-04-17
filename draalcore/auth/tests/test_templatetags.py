#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import MagicMock
from django.conf import settings

from draalcore.auth.templatetags.tags import social_auth
from draalcore.test_utils.basetest import BaseTest


class TemplateTagsTestCase(BaseTest):
    def test_social_auth(self):
        """Test user's social auth status"""

        # No social auth in use
        user = MagicMock(password='pw')
        self.assertTrue(social_auth(user))

        # Social auth in use
        user.password = settings.SOCIAL_AUTH_USER_PASSWORD
        self.assertFalse(social_auth(user))
