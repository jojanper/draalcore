#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User registration actions"""

# System imports
import datetime
import logging
from collections import OrderedDict
from django.utils.timezone import utc
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework.authtoken.models import Token
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login, logout, get_user_model

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
    DISPLAY_NAME = 'Request password request'
    PARAMETERS = OrderedDict([
        ('email', (StringFieldType, NotNullable))
    ])

    def _execute(self):
        form = PasswordResetForm(self.request_obj.data_params)
        if form.is_valid():
            form.save()


class PasswordResetConfirmAction(CreateActionWithParameters):
    ACTION = 'password-reset-confirm'
    DISPLAY_NAME = 'Confirm password reset'
    PARAMETERS = OrderedDict([
        ('uidb64', (StringFieldType, NotNullable)),
        ('token', (StringFieldType, NotNullable)),
        ('password', (StringFieldType, NotNullable))
    ])

    def _execute(self):
        UserModel = get_user_model()
        uidb64 = self.request_obj.data_params['uidb64']
        token = self.request_obj.data_params['token']

        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(self.request_obj.data_params['password'])
            user.save()
            return

        raise ActionError('Password reset unsuccessful')


class PasswordChangeAction(CreateActionWithParameters):
    ACTION = 'password-change'
    DISPLAY_NAME = 'Change password'
    PARAMETERS = OrderedDict([
        ('old_password', (StringFieldType, NotNullable)),
        ('new_password1', (StringFieldType, NotNullable)),
        ('new_password2', (StringFieldType, NotNullable))
    ])

    def _execute(self):
        user = self.request_obj.user

        if user.check_password(self.request_obj.data_params['old_password']):
            password1 = self.request_obj.data_params['new_password1']
            password2 = self.request_obj.data_params['new_password2']
            if password1 != password2:
                raise ActionError('The new passwords did not match')

            user.set_password(password1)
            user.save()
            return

        raise ActionError('Your old password was entered incorrectly. Please enter it again.')
