#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST URLs for API version 2."""

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


# Project imports
from rest_framework import urls as rest_urls
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls import url, include

# Project imports
from draalcore.rest.serializers import (BaseSerializerDataItemHandler,
                                         BaseSerializerDataItemHistoryHandler,
                                         BaseSerializerModelMetaHandler,
                                         BaseSerializerHandler)
from draalcore.rest.actions import (ActionsHandler,
                                     ActionListingsHandler,
                                     ModelsListingHandler)
#from .api import MediaUploadHandler


urlpatterns = [
    url(r'^generic$',
        ModelsListingHandler.as_view(),
        name='rest-api-models'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/meta$',
        BaseSerializerModelMetaHandler.as_view(),
        name='rest-api-model-meta'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/actions$',
        ActionListingsHandler.as_view(),
        name='rest-api-model-actions-listing'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)/history$',
        BaseSerializerDataItemHistoryHandler.as_view(),
        name='rest-api-item-id-history'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)/actions/(?P<action>[A-Za-z0-9\-]+)$',
        ActionsHandler.as_view(),
        name='rest-api-model-actions'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)/actions$',
        ActionListingsHandler.as_view(),
        name='rest-api-item-id-actions-listing'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/(?P<id>\d+)$',
        BaseSerializerDataItemHandler.as_view(),
        name='rest-api-item-id'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)/actions/(?P<action>[A-Za-z0-9\-]+)$',
        ActionsHandler.as_view(),
        name='rest-api-actions'),

    url(r'^generic/(?P<app>[A-Za-z0-9\-_]+)/(?P<model>[A-Za-z0-9]+)$',
        BaseSerializerHandler.as_view(),
        name='rest-api'),

    #url(r'^file-upload$', MediaUploadHandler.as_view(), name='file-uploading'),
]

#
# Token auth API
#
#urlpatterns += [url(r'^token-auth', obtain_auth_token)]

# Enable login via Browsable API
#urlpatterns += [url(r'^rest-api-auth/', include(rest_urls, namespace='rest_framework'))]
