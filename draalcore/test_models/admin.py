#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Register models to admin view"""

# System projects
from django.contrib import admin

# Project imports
from .models import TestModel, TestModel2
from draalcore.models.base_admin import BaseAdmin


class TestModelAdmin(BaseAdmin):
    pass
admin.site.register(TestModel, TestModelAdmin)


class TestModel2Admin(BaseAdmin):
    pass
admin.site.register(TestModel2, TestModel2Admin)
