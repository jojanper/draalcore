#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Add profiling support
from .settings import MIDDLEWARE, INSTALLED_APPS

# http://127.0.0.1:8000/?profile
# MIDDLEWARE += ('draalcore.middleware.profile.InstrumentMiddleware', )

# http://127.0.0.1:8000/?profiler
# MIDDLEWARE += ('draalcore.middleware.profile.ProfileMiddleware', )

# http://127.0.0.1:8000/?__geordi__
# MIDDLEWARE += ('draalcore.middleware.profile.VisorMiddleware', )

# http://127.0.0.1:8000/?sqldump
# MIDDLEWARE += ('draalcore.middleware.sql.SqldumpMiddleware', )

# Required for RPC4Django authenticated method calls
# MIDDLEWARE += ('django.contrib.auth.middleware.RemoteUserMiddleware', )

middleware = 'django.middleware.csrf.CsrfViewMiddleware'
if middleware in MIDDLEWARE:
    MIDDLEWARE = list(MIDDLEWARE)
    MIDDLEWARE.remove(middleware)

# Django debug toolbar
ENABLE_DEBUG_TOOLBAR = False

if ENABLE_DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware', )

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    INTERNAL_IPS = ('127.0.0.1',)

    def custom_show_toolbar(request):
        return True  # Always show toolbar, for example purposes only.

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    }

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        # 'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        # 'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
     ]


LOCAL_TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

SESSION_COOKIE_NAME = 'devsessionid'

SITE_URL = '{}://{}:8080'.format('http', 'localhost')

# Callback URL for 3rd party authentication
EXT_AUTH_CALLBACK_URL = '{}{}'.format(SITE_URL, '/api/apps/auth/public-actions/')

# Redirect URL from callback URL
EXT_AUTH_CALLBACK_RETURN_URL = '/api/apps'
