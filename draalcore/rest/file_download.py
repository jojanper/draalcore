#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File download handling."""

# System imports
import os
import logging
import mimetypes
from django.conf import settings
from django.utils.encoding import smart_str
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper


logger = logging.getLogger(__name__)


class FileDownloader(object):
    def __init__(self, path, filename, local_reference, production, x_accel_redirect):
        self._path = path
        self._filename = filename
        self._local_reference = local_reference
        self._production = production
        self._x_accel_redirect = x_accel_redirect

    @classmethod
    def create(cls, path, filename, local_reference=None):
        production = getattr(settings, 'PRODUCTION_ENVIRONMENT', False)
        x_accel_redirect = getattr(settings, 'X_ACCEL_REDIRECT', '')
        if local_reference is None:
            local_reference = path

        return cls(path, filename, local_reference, production, x_accel_redirect)

    def download(self):
        content_type = mimetypes.guess_type(self._path)[0]

        if not self._production or not self._x_accel_redirect:
            # Django serves the media, not optimal for production environment
            wrapper = FileWrapper(open(self._path, "r"))
            response = StreamingHttpResponse(wrapper, content_type=content_type)
        else:
            # Let the web server serve the media
            response = StreamingHttpResponse(content_type=content_type)

            # Sets the URI for web server to serve
            #
            # This is Nginx specific configuration. X-accel allows for internal
            # redirection to a location determined by a header returned from
            # a backend.
            media_path = self._x_accel_redirect + '{0}'
            path_prefix = os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_MEDIA_ROOT)
            ref = self._local_reference.replace(path_prefix, '')
            response['X-Accel-Redirect'] = media_path.format(ref)

        response['Content-Length'] = os.path.getsize(self._path)
        response['Content-Disposition'] = 'attachment; filename="%s"' % (smart_str(self._filename))

        return response
