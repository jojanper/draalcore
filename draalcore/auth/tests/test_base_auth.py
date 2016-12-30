#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import MagicMock

from draalcore.test_utils.basetest import BaseTestUser
from draalcore.auth.sites.base_auth import Base3rdPartyAuth


class BaseAuthTestCase(BaseTestUser):

    def test_authenticate(self):
        """User is authenticated using response from social site"""

        # GIVEN authentication credentials
        request = MagicMock()
        kwargs = {'username': self.username, 'password': self.password}

        # WHEN user is authenticated
        user = Base3rdPartyAuth().authenticate(request, **kwargs)

        # THEN it should succeed
        self.assertEqual(user.id, self.user.id)
