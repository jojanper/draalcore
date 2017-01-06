#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.apps import AppConfig


class AdminConfig(AppConfig):
    name = 'draalcore.test_apps.admin'
    label = 'draalcore.test_apps.admin'

    public_app = True
    display_name = 'admin'
    actions = []

    def ready(self):
        from .actions import CreateNewAction

        self.actions = [CreateNewAction]
