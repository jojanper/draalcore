#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User registration actions"""

# System imports
from django.conf import settings
from django.db import transaction
from collections import OrderedDict

# Project imports
from draalcore.mailer import Mailer
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
        obj = self.MODEL.objects.register_user(**self.request_obj.data_params)
        Mailer(settings.ACCOUNT_ACTIVATION_SUBJECT).send_message('', [obj.user.email])
        return 'Check your email! An activation link has been sent to the email ' \
            'address you supplied, along with instructions for activating your account.'
