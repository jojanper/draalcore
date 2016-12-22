#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base views, permissions and response definitions for ReST API"""

# System imports
import sys
import logging
from django.http.response import HttpResponseBase
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authentication import (SessionAuthentication,
                                           BasicAuthentication,
                                           TokenAuthentication)

# Project imports
from draalcore.exceptions import AppException
from draalcore.rest.request_data import RequestData
from draalcore.rest.response_data import ResponseData
from draalcore.rest.auth import RestAuthentication, SessionNoCSRFAuthentication
from draalcore.middleware.current_user import CurrentUserMiddleware


logger = logging.getLogger(__name__)


def api_response(response):
    """Response generation for ReST API calls"""

    # Errors present
    if response.message:
        messages = response.message
        if not isinstance(messages, list):
            messages = [messages]

        # Report the errors
        return Response({'errors': messages}, status=status.HTTP_400_BAD_REQUEST)

    # All OK
    return Response(response.data) if not isinstance(response.data, HttpResponseBase) else response.data


class AppActionsPermission(BasePermission):
    """
    Custom permission class where permission can only be applied against HTTP method.
    """

    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': [],
        'PATCH': [],
        'DELETE': []
    }

    def get_required_permissions(self, method, model_cls):
        """
        Given HTTP method, return the list of permission
        codes that the user is required to have.
        """
        return self.perms_map.get(method, [])

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method, None)

        if (request.user and (request.user.is_authenticated() or not self.authenticated_users_only) and
                request.user.has_perms(perms)):
            return True

        return False


class RestAPIBaseView(APIView):
    """ReST API base class with token and session authentication"""

    permission_classes = (IsAuthenticated, AppActionsPermission,)
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    def _execute(self, request, *args, **kwargs):
        try:
            try:
                # Assign current user for other modules to use
                CurrentUserMiddleware().process_request(request)

                # Get HTTP method
                fn = getattr(self, '_' + request.method.lower())
            except AttributeError:
                msg = 'Implementation missing for %s' % (request.method)
                return api_response(ResponseData(message=msg))

            # Execute HTTP method and return response
            req_data = RequestData(request, *args, **kwargs)
            return api_response(fn(req_data))

        except AppException as e:
            return api_response(ResponseData(message=e.args[0]))


class RestAPIBasicAuthView(RestAPIBaseView):
    """ReST API base class with token, session, and basic auth authentication"""

    authentication_classes = (TokenAuthentication, SessionAuthentication,
                              RestAuthentication, BasicAuthentication,)

    def get_authenticate_header(self, request):
        """
        Failure scheme to follow in case authentication fails.

        Current scheme will enable WWW-Authenticate in the HTTP response
        header, browser responds to this header by popping up the credentials
        dialog and then sends the login credentials back to server (which then
        enables the backend server to continue the execution as user has been
        now authenticated).
        """
        return self.authentication_classes[2]().authenticate_header(request)
