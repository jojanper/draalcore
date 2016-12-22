#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RequestData tests"""

# System imports
import os
import logging
from mock import MagicMock, patch

# Project imports
from ..request_data import RequestData
from draalcore.test_utils.basetest import BaseTest


logger = logging.getLogger(__name__)


class RequestDataTestCase(BaseTest):
    """RequestData object."""

    def test_creation_none_request(self):
        """Request parameter is None"""
        obj = RequestData(None)

        self.assertEqual(obj.data_params, {})
        self.assertEqual(obj.url_params, '')

    def test_request_repr(self):
        """Request has printable representation."""
        obj = RequestData(MagicMock())
        self.assertTrue(len(repr(obj)) > 0)

    def test_has_url_param(self):
        """Existence of URL parameter value is checked"""

        # GIVEN URL parameter in HTTP request
        data = dict(key='value')
        mock_request = MagicMock(GET=data)
        obj = RequestData(mock_request)

        # WHEN checking existence of a key from URL parameters
        status = obj.has_url_param('key', 'value')

        # THEN is should succeed
        self.assertTrue(status)

        # -----

        # WHEN checking non-existing key from URL parameters
        status = obj.has_url_param('key2', 'value')

        # THEN is should fail
        self.assertFalse(status)
