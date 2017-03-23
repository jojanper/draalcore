#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Authentication ReST URLs"""

# System imports
from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token

# Project imports
from .login import LoginHandler, LogoutHandler


__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2017"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


urlpatterns = [
    # Sign-in
    url(r'^login', LoginHandler.as_view(), name='rest-api-login'),

    # Sign-out
    url(r'^logout', LogoutHandler.as_view(), name='rest-api-logout'),

    # Token auth API
    url(r'^token', obtain_auth_token)
]
