#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base views"""

# System imports
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt


class BaseView(View):
    """Base for class based views"""
    pass


class BaseViewNoCSRF(BaseView):
    """"Base view that does not require CSRF checking"""
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(BaseViewNoCSRF, self).dispatch(*args, **kwargs)
