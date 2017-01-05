#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST URLs for accessing system models and data"""

# Project imports
from django.conf import settings
from django.conf.urls import url

# Project imports
from draalcore.rest.serializers import (BaseSerializerDataItemHandler,
                                        BaseSerializerDataItemHistoryHandler,
                                        BaseSerializerModelMetaHandler,
                                        BaseSerializerHandler)
from draalcore.rest.actions import (ActionsHandler,
                                    ActionListingsHandler,
                                    ModelsListingHandler)

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


prefix = getattr(settings, 'DRAALCORE_REST_SYSTEM_BASE_PREFIX', 'system')
app_prefix = '{}/(?P<app>[A-Za-z0-9\-_]+)'.format(prefix)
model_prefix = '{}/(?P<model>[A-Za-z0-9]+)'.format(app_prefix)


urlpatterns = [

    url(r'{}/(?P<id>\d+)/actions/(?P<action>[A-Za-z0-9\-]+)$'.format(model_prefix),
        ActionsHandler.as_view(),
        name='rest-api-model-id-action'),

    url(r'{}/actions/(?P<action>[A-Za-z0-9\-]+)$'.format(model_prefix),
        ActionsHandler.as_view(),
        name='rest-api-model-action'),

    url(r'{}/(?P<id>\d+)/actions$'.format(model_prefix),
        ActionListingsHandler.as_view(),
        name='rest-api-model-id-actions-listing'),

    url(r'{}/(?P<id>\d+)/history$'.format(model_prefix),
        BaseSerializerDataItemHistoryHandler.as_view(),
        name='rest-api-model-id-history'),

    url(r'{}/(?P<id>\d+)$'.format(model_prefix),
        BaseSerializerDataItemHandler.as_view(),
        name='rest-api-model-id'),

    url(r'{}/actions$'.format(model_prefix),
        ActionListingsHandler.as_view(),
        name='rest-api-model-actions-listing'),

    url(r'{}/meta$'.format(model_prefix),
        BaseSerializerModelMetaHandler.as_view(),
        name='rest-api-model-meta'),

    url(r'{}/actions$'.format(app_prefix),
        ActionListingsHandler.as_view(),
        name='rest-api-app-actions'),

    url(r'{}$'.format(model_prefix),
        BaseSerializerHandler.as_view(),
        name='rest-api-model'),

    url(r'{}$'.format(prefix),
        ModelsListingHandler.as_view(),
        name='rest-api'),
]
