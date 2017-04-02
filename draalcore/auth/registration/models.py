#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Registration model(s)"""

# System imports
import hashlib
import random
from django.db import models
from django.contrib.auth.models import User

# Project imports
from draalcore.models.base_model import ModelLogger, ModelBaseManager


class UserAccountManager(ModelBaseManager):

    def register_user(self, **kwargs):
        new_user = User.objects.create_user(kwargs['username'], kwargs['email'], kwargs['password'])
        new_user.first_name = kwargs['first_name']
        new_user.last_name = kwargs['last_name']
        new_user.is_active = False
        new_user.save()

        # user_account_profile = self.create_account_profile(new_user)

    def create_account_profile(self, user):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = hashlib.sha1(salt + username).hexdigest()

        return self.create(user=user, activation_key=activation_key)


class UserAccountProfile(ModelLogger):
    """User account management data"""

    EXTERNAL_API = False

    user = models.OneToOneField(User, help_text='User', related_name='account_profiles')
    activation_key = models.CharField(max_length=40, help_text='Account activation key')

    objects = UserAccountManager()

    class Meta:
        db_table = 'useraccount'

    def __str__(self):
        return "{}({},{},{})".format(self.__class__.__name__, self.id, self.user, self.activation_key)
