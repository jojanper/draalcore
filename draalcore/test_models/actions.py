#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test action implementations"""

# Project imports
from draalcore.exceptions import ActionError
from ..rest.actions import CreateAction, AbstractModelGetAction, AbstractModelItemGetAction
from .models import TestModel, TestModel2


class CreateNewAction(CreateAction):
    ACTION = 'create-new'
    MODEL = TestModel2

    def _execute(self):
        return {'data': 'abcd'}


class CreateNewAction2(CreateAction):
    ACTION = 'create-new'
    MODEL = TestModel


class GetAction(AbstractModelGetAction):
    ACTION = 'get'
    MODEL = TestModel2

    def execute(self):
        return {'data': 'dcba'}


class GetAction2(AbstractModelItemGetAction):
    ACTION = 'get2'
    MODEL = TestModel2

    def _execute(self, model_obj):
        raise ActionError(['error1', 'error2'])
