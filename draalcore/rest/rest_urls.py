#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST URLs for accessing system models and data"""

# Project imports
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


urlpatterns = [

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)/actions/(?P<action>[A-Za-z0-9\-]+)$',
        ActionsHandler.as_view(),
        name='rest-api-model-actions'),

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/actions/(?P<action>[A-Za-z0-9\-]+)$',
        ActionsHandler.as_view(),
        name='rest-api-actions'),

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)/actions$',
        ActionListingsHandler.as_view(),
        name='rest-api-item-id-actions-listing'),

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)/history$',
        BaseSerializerDataItemHistoryHandler.as_view(),
        name='rest-api-item-id-history'),

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)$',
        BaseSerializerDataItemHandler.as_view(),
        name='rest-api-item-id'),

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/actions$',
        ActionListingsHandler.as_view(),
        name='rest-api-model-actions-listing'),

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/meta$',
        BaseSerializerModelMetaHandler.as_view(),
        name='rest-api-model-meta'),

    url(r'(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)$',
        BaseSerializerHandler.as_view(),
        name='rest-api'),

    url(r'$',
        ModelsListingHandler.as_view(),
        name='rest-api-models'),
]
