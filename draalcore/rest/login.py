#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sign-in and sign-out handling"""

# System imports
from django.contrib.auth import authenticate, login, logout

# Project imports
from .response_data import ResponseData
from .base_serializers import UserModelSerializer
from .handlers import PostMixin, RestAPINoAuthView
from draalcore.middleware.login import AutoLogout


class LoginHandler(PostMixin, RestAPINoAuthView):
    def _post(self, request_obj):
        user = authenticate(**request_obj.request.data)
        if user:
            login(request_obj.request, user)
            data = UserModelSerializer(user).data
            data['expires'] = AutoLogout.expires()
            return ResponseData(data)

        return ResponseData(message='Invalid username and/or password.')


class LogoutHandler(PostMixin, RestAPINoAuthView):
    def _post(self, request_obj):
        logout(request_obj.request)
        return ResponseData('Sign-out successful')
