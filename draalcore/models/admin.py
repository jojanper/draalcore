#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Register models to admin view."""

# System imports
from django.contrib import admin
from django.contrib.admin.models import LogEntry

# Project imports
from draalcore.models.admin_log import LogEntryAdmin


admin.site.register(LogEntry, LogEntryAdmin)
