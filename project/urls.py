#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test app URLs"""

from django.contrib import admin
from django.conf import settings
from django.shortcuts import render
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from draalcore.views.baseviews import BaseView

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

admin.autodiscover()


class DummyView(BaseView):
    def get(self, request, *args, **kwargs):
        return render(request, '')


urlpatterns = [
    url(r'^$', DummyView.as_view(), name='main-view'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('draalcore.rest.urls')),
    url(r'^login/$', auth_views.login, {'template_name': ''}, name='auth-login'),
    url(r'^settings$', DummyView.as_view(), name='settings-view'),
]

# ReST APIs for testing
if settings.TEST_URLS:
    urlpatterns += [url(r'^test-api/', include('draalcore.test_apps.test_models.urls'))]

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [url(r'^djdt/', include(debug_toolbar.urls))]
