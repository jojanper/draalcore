#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Admin level actions"""

# Project imports
from draalcore.rest.actions import CreateAction
from draalcore.test_apps.test_models.models import TestModel2


class CreateNewAction(CreateAction):
    ACTION = 'create-new'
    MODEL = TestModel2

    def _execute(self):
        return {'data': 'abcd'}