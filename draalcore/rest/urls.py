#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST URLs"""

# System imports
from django.conf.urls import url, include

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015-2017,2021"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


urlpatterns = [
    # Access to system models and data
    url(r'^', include('draalcore.rest.rest_urls')),
]
