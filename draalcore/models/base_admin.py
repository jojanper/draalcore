#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base admin classes"""

# System imports
import logging
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import escape


logger = logging.getLogger(__name__)


class BaseAdmin(admin.ModelAdmin):
    """
    Base class for viewing a model in admin view.
    """

    ordering = ('id',)

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        obj.save()

    def has_add_permission(self, request):
        """Change return value to True if new item need to be added through admin"""
        return True

    def has_delete_permission(self, request, obj=None):
        """Deleting instance should be allowed"""
        return True

    def get_queryset(self, request):
        """Use admin manager so that also deleted items are visible."""
        qs = self.model.admin_objects.get_queryset()
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)

        return qs
