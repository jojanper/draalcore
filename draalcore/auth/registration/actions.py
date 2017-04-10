#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User registration actions"""

# System imports
from django.conf import settings
from django.db import transaction
from collections import OrderedDict
from django.contrib.auth.models import User
from django.template.loader import render_to_string

# Project imports
from draalcore.mailer import Mailer
from draalcore.exceptions import ModelManagerError
from draalcore.auth.models import UserAccountProfile
from draalcore.rest.actions import CreateActionWithParameters
from draalcore.models.fields import StringFieldType, NotNullable


class RegisterUserAction(CreateActionWithParameters):
    ACTION = 'register'
    MODEL = UserAccountProfile
    DISPLAY_NAME = 'Register new user'
    PARAMETERS = OrderedDict([
        ('username', (StringFieldType, NotNullable)),
        ('email', (StringFieldType, NotNullable)),
        ('password', (StringFieldType, NotNullable)),
        ('first_name', (StringFieldType, NotNullable)),
        ('last_name', (StringFieldType, NotNullable))
    ])

    @transaction.atomic
    def _execute(self):
        username = self.request_obj.data_params['username']
        if User.objects.filter(username=username).exists():
            err_text = 'Username {} is already reserved, please select another'.format(username)
            raise ModelManagerError(err_text)

        obj = self.MODEL.objects.register_user(**self.request_obj.data_params)
        message = self._get_email_message(obj)
        Mailer(settings.ACCOUNT_ACTIVATION_SUBJECT).send_message(message, [obj.user.email])
        return 'Check your email! An activation link has been sent to the email ' \
            'address you supplied, along with instructions for activating your account.'

    def _get_email_message(self, model_obj):
        context = {
           'activation_key': model_obj.activation_key,
           'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
           'activation_url': settings.ACTIVATION_URL
        }

        return render_to_string('registration/activation_email.txt', context)


class ActivateUserAction(CreateActionWithParameters):
    ACTION = 'activate'
    MODEL = UserAccountProfile
    DISPLAY_NAME = 'Activate user account'
    PARAMETERS = OrderedDict([
        ('activation_key', (StringFieldType, NotNullable))
    ])

    @transaction.atomic
    def _execute(self):
        return self.MODEL.objects.activate_user(**self.request_obj.data_params)
