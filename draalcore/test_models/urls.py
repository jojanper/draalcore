#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST API URLs for testing"""

# System imports
from django.conf.urls import url

from draalcore.rest.mixins import GetMixin, PutMixin, PostMixin, PatchMixin, DeleteMixin
from draalcore.rest.handlers import FileUploadHandler, RestAPIBasicAuthView, AppActionsPermission

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2015"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


class TestUploadHandler(FileUploadHandler):
    """File upload handler that does not have upload method defined"""
    UPLOAD_METHOD = 'none'


class TestUploadHandler2(FileUploadHandler):
    """File upload handler that includes also upload method"""
    def _upload(self, filename, file_obj, request_obj):
        pass


class FileUploadPermission(AppActionsPermission):
    """Custom permission for file upload"""
    perms_map = {
        'POST': ['upload-permission']
    }


class TestUploadHandler3(FileUploadHandler):
    """File upload handler with custom permission"""
    permission_classes = (FileUploadPermission, )


class InvalidAPIHandler(GetMixin, PutMixin, PatchMixin, PostMixin, DeleteMixin, RestAPIBasicAuthView):
    """API handler that does not implement any HTTP methods"""
    pass


urlpatterns = [
    url(r'^file-upload-invalid$', TestUploadHandler.as_view(), name='test-file-upload'),
    url(r'^file-upload-valid$', TestUploadHandler2.as_view(), name='test-file-upload2'),
    url(r'^file-upload-permission$', TestUploadHandler3.as_view(), name='test-file-upload3'),

    url(r'^invalid-http-api$', InvalidAPIHandler.as_view(), name='invalid-http-api')
]
