#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Middleware utilities"""

# System imports
from abc import ABC

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2021"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


class BaseMiddleware(ABC):
    """
    Base class for middleware processing.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        response2 = response if response else self.get_response(request)
        return self.process_response(request, response2)

    def process_request(self, request):
        """Implementation may override default"""
        return None

    def process_response(self, request, response):
        """Implementation may override default"""
        return response
