#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Registration model(s)"""

# System imports
import re
import hashlib
import random
import datetime
import logging
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now as datetime_now
try:
    bool(type(unicode))
except NameError:
    unicode = str

# Project imports
from draalcore.exceptions import ModelManagerError
from draalcore.middleware.current_user import set_current_user
from draalcore.models.base_model import ModelLogger, ModelBaseManager


SHA1_RE = re.compile('^[a-f0-9]{40}$')
logger = logging.getLogger(__name__)


class UserAccountManager(ModelBaseManager):

    def register_user(self, **kwargs):
        new_user = User.objects.create_user(kwargs['username'], kwargs['email'], kwargs['password'])
        new_user.first_name = kwargs['first_name']
        new_user.last_name = kwargs['last_name']
        new_user.is_active = False
        new_user.save()

        return self.create_account_profile(new_user)

    def create_account_profile(self, user):
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = hashlib.sha1('{}{}'.format(salt, username).encode('utf-8')).hexdigest()

        set_current_user(user)
        return self.create(user=user, activation_key=activation_key)

    def activate_user(self, activation_key):

        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                account = self.get(activation_key=activation_key,
                                   account_status=self.model.ACCOUNT_ACTIVE)
            except self.model.DoesNotExist:
                raise ModelManagerError('Activation key not found')

            if not account.activate_account():
                raise ModelManagerError('Activation key expired')

            return True

        raise ModelManagerError('Invalid activation key')


class UserAccountProfile(ModelLogger):
    """User account management data"""

    EXTERNAL_API = False
    ANONYMOUS_ALLOWED = True

    # Model visibility status, deleted items are not shown to user
    ACCOUNT_ACTIVE = 'Active'
    ACCOUNT_ACTIVATED = 'Activated'
    ACCOUNT_EXPIRED = 'Expired'
    ACCOUNT_CHOICES = (
        (ACCOUNT_ACTIVE, ACCOUNT_ACTIVE),
        (ACCOUNT_ACTIVATED, ACCOUNT_ACTIVATED),
        (ACCOUNT_EXPIRED, ACCOUNT_EXPIRED),
    )

    user = models.OneToOneField(User, help_text='User', related_name='account_profiles')
    activation_key = models.CharField(max_length=40, help_text='Account activation key')
    account_status = models.CharField(max_length=24, choices=ACCOUNT_CHOICES,
                                      default=ACCOUNT_ACTIVE, help_text='Account status')

    objects = UserAccountManager()

    class Meta:
        db_table = 'useraccount'

    def __str__(self):
        return "{}({},{},{})".format(self.__class__.__name__, self.id, self.user, self.account_status)

    @property
    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.user.date_joined + expiration_date <= datetime_now()

    def activate_account(self):
        user = self.user
        self.modified_by = user
        if not self.activation_key_expired:
            user.is_active = True
            user.save()
            self.set_values(account_status=self.ACCOUNT_ACTIVATED)
            return True

        return False
