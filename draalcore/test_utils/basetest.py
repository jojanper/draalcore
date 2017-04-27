#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base utility classes for testing"""


# System imports
import sys
from django.test import TestCase
from django.contrib.auth.models import User, Permission

from draalcore.test_utils.rest_api import GenericAPI, AuthAPI


def create_user(username, password, email):

    user_mgr = User.objects

    users = user_mgr.filter(username=username)
    if users.count() == 0:
        user = user_mgr.create_user(username, email, password)
        user.save()
    else:
        user = users[0]

    return user


class BaseTest(TestCase):
    """Base test class"""

    def setUp(self):
        super(BaseTest, self).setUp()
        self.basetest_initialize()

    def tearDown(self):
        super(BaseTest, self).tearDown()

    def basetest_initialize(self):
        pass

    def logging(self, message):
        sys.stderr.write('DEBUG: ' + str(message) + '\n')

    def validate_user_response(self, data):
        self.assertTrue('display' in data)
        self.assertTrue('id' in data)
        self.assertTrue('email' in data)
        self.assertTrue('expires' in data)
        self.assertTrue('token' in data)


class BaseTestUser(BaseTest):
    """Base test class with user login"""

    def setUp(self):
        super(BaseTestUser, self).setUp()

        self.username = 'user'
        self.password = 'user-password'
        self.email = 'user@gmail.com'

        self.user = create_user(self.username, self.password, self.email)
        self.user.first_name = self.username
        self.user.last_name = self.username
        self.user.save()
        self.signin = self.login()

        self.api = GenericAPI(self)
        self.auth_api = AuthAPI(self)

        self.initialize()

    def initialize(self):
        pass

    def tearDown(self):
        super(BaseTestUser, self).tearDown()
        self.logout()
        if self.signin:
            self.user.delete()

    def login(self):
        self.signin = self.client.login(username=self.username, password=self.password)
        return self.signin

    def logout(self):
        self.client.logout()
        self.signin = False

    def enable_superuser(self):
        self.logout()
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.login()

    def disable_superuser(self):
        self.logout()
        self.user.is_staff = False
        self.user.is_superuser = False
        self.user.save()
        self.login()

    def remove_permission(self, permission):
        obj = self.user.groups.all()[0]
        obj.permissions.remove(Permission.objects.get(codename=permission))

    def add_permission(self, permission):
        obj = self.user.groups.all()[0]
        obj.permissions.add(Permission.objects.get(codename=permission))
