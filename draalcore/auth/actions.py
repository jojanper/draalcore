#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Admin level actions"""

# System imports
from collections import OrderedDict

# Project imports
from draalcore.exceptions import DataParsingError
from draalcore.rest.actions import CreateAction
from draalcore.auth.models import UserAccount
from draalcore.models.fields import StringFieldType


class Nullable(object):
    null = True


class NotNullable(Nullable):
    null = False


class RegisterUserAction(CreateAction):
    ACTION = 'register'
    MODEL = UserAccount
    PARAMETERS = OrderedDict([
        ('username', (StringFieldType, NotNullable)),
        ('email', (StringFieldType, NotNullable)),
        ('password', (StringFieldType, NotNullable)),
        ('first_name', (StringFieldType, NotNullable)),
        ('last_name', (StringFieldType, NotNullable))
    ])

    def _execute(self):
        errors = []
        for key in self.PARAMETERS.iterkeys():
            if key not in self.request_obj.data_params:
                errors.append(key)

        if errors:
            raise DataParsingError('Following items are missing from POST data: {}'.format(', '.join(errors)))

        for key, params in self.PARAMETERS.iteritems():
            params[0].validate_type(key, self.request_obj.data_params.get(key), params[1])

        print(self.request_obj.data_params)

        return 'user registered'
