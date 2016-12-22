#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test app URLs"""

from django.contrib import admin
from django.conf import settings
from django.shortcuts import render
from django.conf.urls import include, url

from draalcore.views.baseviews import BaseView

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

admin.autodiscover()


class SettingsView(BaseView):
    def get(self, request, *args, **kwargs):
        return render(request, '')


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^apiv2/', include('draalcore.rest.urls')),
    url(r'^settings$', SettingsView.as_view(), name='settings-view'),
]

# ReST APIs for testing
if settings.TEST_URLS:
    urlpatterns += [url(r'^test-api/', include('draalcore.test_models.urls'))]

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [url(r'^djdt/', include(debug_toolbar.urls))]
