#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3rd party authentication endpoint URLs"""

# System imports
from django.conf.urls import url, include

# Project imports
from .views import ExtAuthView, ExtAuthCallbackView

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2017"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


urlpatterns = [

    # OAuth2 callback URL
    url(r'^ext-auth/oauth2-callback/(?P<provider>[^/]+)$', ExtAuthCallbackView.as_view(), name='oauth2-callback'),

    # 3rd party sign-in
    url(r'^ext-auth/(?P<provider>[^/]+)$', ExtAuthView.as_view(), name='ext-auth-login'),
]
