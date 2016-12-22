#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File upload and download handling"""

# System imports
import os
import logging
from rest_framework.parsers import FileUploadParser
from django.core.files.uploadedfile import UploadedFile

# Project imports
from draalcore.exceptions import AppException
from draalcore.rest.mixins import PostMixin
from draalcore.rest.response_data import ResponseData
from draalcore.rest.views import RestAPIBasicAuthView


logger = logging.getLogger(__name__)


class NginxUploadedFile(UploadedFile):
    """
    Construct File instances that point at the uploaded (handled by Nginx) files
    and have the metadata parsed out of the passed parameters.
    """

    def __init__(self, path, name, content_type, size, charset):
        file = open(path, 'rb')
        super(NginxUploadedFile, self).__init__(file, name, content_type, size, charset)

    def temporary_file_path(self):
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except OSError as e:
            if e.errno != 2:
                # Means the file was moved or deleted before the tempfile
                # could unlink it. Still sets self.file.close_called and
                # calls self.file.file.close() before the exception
                raise


class FileLoader(object):

    def __init__(self, request, file_identifier):
        self._request = request
        self.file_identifier = file_identifier

    @property
    def request(self):
        return self._request

    def get_upload_file(self):
        """Application handles the file upload"""
        if self.request.FILES is None or self.request.FILES.get(self.file_identifier, None) is None:
            raise AppException('No files attached')

        return UploadedFile(self.request.FILES.get(self.file_identifier, None))

    def get_nginx_file(self):
        """Nginx server handled the upload, determine the file details from POST parameters"""

        path = self.request.POST.get(self.file_identifier + '.path', None)
        if path:
            logger.debug('Nginx upload file {} found'.format(path))

            file_size = os.path.getsize(path)
            filename = self.request.POST.get(self.file_identifier + '.name', 'noname')
            content_type = self.request.POST.get(self.file_identifier + '.content_type', '')
            return NginxUploadedFile(path, filename, content_type, file_size, 'utf8')

        # This ensures backward compatibility
        return self.get_upload_file()

    def get_file(self):
        """
        Interface for receiving uploaded files from clients. This is Nginx specific configuration
        where the web server first handles the files upload, stores those to a directory and then
        lets the Django app to handle the file from there on. Includes also backwards compatibility
        to app based upload handling.
        """
        obj = self.get_nginx_file()
        name = self.request.POST.get('filename', obj.name)
        obj.name = obj.name.replace('(', '').replace(')', '')
        return obj


class FileUploadHandler(PostMixin, RestAPIBasicAuthView):
    """
    ReST base class for file uploading.

    Implementing class must have method defined by UPLOAD_METHOD.
    """

    parser_classes = (FileUploadParser, )
    UPLOAD_METHOD = '_upload'

    def _post(self, request_obj):
        request = request_obj.request

        try:
            fn = getattr(self, self.UPLOAD_METHOD)
        except AttributeError:
            raise AppException('Upload implementation missing, please contact application support')

        obj = FileLoader(request, 'file').get_file()

        return ResponseData(fn(obj.name, obj, request_obj))
