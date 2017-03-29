#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User registration actions"""

# System imports
from collections import OrderedDict

# Project imports
from draalcore.auth.models import UserAccount
from draalcore.rest.actions import CreateActionWithParameters
from draalcore.models.fields import StringFieldType, NotNullable


class RegisterUserAction(CreateActionWithParameters):
    ACTION = 'register'
    MODEL = UserAccount
    DISPLAY_NAME = 'Register new user'
    PARAMETERS = OrderedDict([
        ('username', (StringFieldType, NotNullable)),
        ('email', (StringFieldType, NotNullable)),
        ('password', (StringFieldType, NotNullable)),
        ('first_name', (StringFieldType, NotNullable)),
        ('last_name', (StringFieldType, NotNullable))
    ])

    def _execute(self):
        return 'user registered'
