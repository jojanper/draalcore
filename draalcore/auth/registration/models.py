#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Registration model(s)"""

# System imports
from django.db import models
from django.contrib.auth.models import User

# Project imports
from draalcore.models.base_model import ModelLogger, ModelBaseManager


class UserAccountManager(ModelBaseManager):
    pass


class UserAccount(ModelLogger):
    """User account management data"""

    EXTERNAL_API = False

    user = models.OneToOneField(User, help_text='User', related_name='accounts')
    activation_key = models.CharField(max_length=40, help_text='Account activation key')

    objects = UserAccountManager()

    class Meta:
        db_table = 'useraccount'

    def __str__(self):
        return "{}({},{},{})".format(self.__class__.__name__, self.id, self.user, self.activation_key)
