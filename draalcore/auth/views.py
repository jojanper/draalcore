#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interface for 3rd party authentication"""

# System imports
from django.views.generic.base import View
from django.http import HttpResponseRedirect

# Project imports
from .sites import AuthFactory


__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


class ExtAuthView(View):
    """3rd party authentication interface"""

    def get(self, request, *args, **kwargs):
        obj = AuthFactory.create(kwargs['provider'])
        return HttpResponseRedirect(obj.get_authorize_url(request))


class ExtAuthCallbackView(View):
    """3rd party authentication callback interface"""

    def get(self, request, *args, **kwargs):
        obj = AuthFactory.create(kwargs['provider'])
        return obj.authorize(request)
