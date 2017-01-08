#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mixins for testing."""

# Project imports
from draalcore.test_apps.test_models.models import TestModel, TestModel2, TestModel3, TestModel4, TestModel5


class TestModelMixin(object):
    def initialize(self):
        self.app_label = 'test_models'
        self.model_name = TestModel._meta.db_table
        self.model_name2 = TestModel2._meta.db_table
        self.model_name3 = TestModel3._meta.db_table
        self.model_name4 = TestModel4._meta.db_table

        # Fetch model meta so that user get_current_user() gets registered with valid user
        self.api.meta(self.app_label, self.model_name2)

        self.obj1 = TestModel.objects.create(name='test')
        self.obj2 = TestModel2.objects.create(name='test2', model1=self.obj1)
        self.obj3 = TestModel3.objects.create(name='test3')
        self.obj4 = TestModel4.objects.create(name='test4')
        self.obj5 = TestModel5.objects.create(name='test5')
