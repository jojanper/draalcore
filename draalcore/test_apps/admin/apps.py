#!/usr/bin/env python
# -*- coding: utf-8 -*-

from draalcore.app_config import BaseAppConfig


class AdminConfig(BaseAppConfig):
    default = True
    name = 'draalcore.test_apps.admin'
    label = 'draalcore_test_apps_admin'
    display_name = 'admin'

    def ready(self):
        from .actions import CreateNewAction, CreateNew2Action

        self.actions = [CreateNewAction]
        self.noauth_actions = [CreateNew2Action]
