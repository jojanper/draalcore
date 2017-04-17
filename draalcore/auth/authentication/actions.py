#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User registration actions"""

# System imports
import datetime
import logging
from collections import OrderedDict
from django.utils.timezone import utc
from rest_framework.authtoken.models import Token
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import authenticate, login, logout

# Project imports
from draalcore.exceptions import ActionError
from draalcore.middleware.login import AutoLogout
from draalcore.rest.base_serializers import UserModelSerializer
from draalcore.rest.actions import CreateActionWithParameters, CreateAction
from draalcore.models.fields import StringFieldType, NotNullable


logger = logging.getLogger(__name__)


class LoginAction(CreateActionWithParameters):
    ACTION = 'login'
    DISPLAY_NAME = 'Sign-in'
    PARAMETERS = OrderedDict([
        ('username', (StringFieldType, NotNullable)),
        ('password', (StringFieldType, NotNullable))
    ])

    def _execute(self):
        user = authenticate(**self.request_obj.data_params)
        if user:
            login(self.request_obj.request, user)
            data = UserModelSerializer(user).data
            data['expires'] = AutoLogout.expires()
            data['token'] = self._get_token(user)
            return data

        raise ActionError('Invalid username and/or password')

    def _get_token(self, user):
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            # Update the created time of the token to keep it valid
            token.created = datetime.datetime.utcnow().replace(tzinfo=utc)
            token.save()

        return {'token': token.key}


class LogoutAction(CreateAction):
    ACTION = 'logout'
    DISPLAY_NAME = 'Sign-out'

    def _execute(self):
        logout(self.request_obj.request)
        return 'Sign-out successful'


class TokenAction(LoginAction):
    ACTION = 'token'
    DISPLAY_NAME = 'Get authentication token'

    def _execute(self):
        user = authenticate(**self.request_obj.data_params)
        if user:
            return self._get_token(user)

        raise ActionError('Invalid username and/or password')


class PasswordResetAction(CreateActionWithParameters):
    ACTION = 'password-reset'
    DISPLAY_NAME = 'Reset password'
    PARAMETERS = OrderedDict([
        ('email', (StringFieldType, NotNullable))
    ])

    def _execute(self):
        form = PasswordResetForm(self.request_obj.data_params)
        if form.is_valid():
            form.save()
