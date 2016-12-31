#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST URLs"""

# Project imports
from django.conf.urls import url, include
from rest_framework import urls as rest_urls
from rest_framework.authtoken.views import obtain_auth_token


__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


urlpatterns = [
    # Token auth API
    url(r'^token-auth', obtain_auth_token),

    # Enable login via Browsable API
    url(r'^browsable-auth/', include(rest_urls, namespace='rest_framework')),

    # Access to system models and data
    url(r'^system/', include('draalcore.rest.rest_urls')),
]
