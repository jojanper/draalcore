#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST URLs"""

# System imports
from django.conf.urls import url, include
from rest_framework import urls as rest_urls


__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015-2017"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


urlpatterns = [
    # Access to system models and data
    url(r'^', include('draalcore.rest.rest_urls')),

    # Auth API
    url(r'^auth/', include('draalcore.rest.auth_urls')),

    # Enable login via Browsable API
    url(r'^browsable-auth/', include(rest_urls, namespace='rest_framework')),
]
