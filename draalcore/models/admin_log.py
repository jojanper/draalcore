#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""View all log entries in the admin.

Adapted from https://djangosnippets.org/snippets/2484/
"""

# System imports
from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch


class LogEntryAdmin(admin.ModelAdmin):

    date_hierarchy = 'action_time'

    readonly_fields = ['user', 'content_type', 'object_id', 'change_message', 'object_repr', 'action_flag']

    list_filter = [
        'content_type'
    ]

    search_fields = [
        'user__username',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            try:
                link = u'<a href="%s">%s</a>' % (
                    reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                    escape(obj.object_repr),
                    )
            except NoReverseMatch:
                link = u'Unknown'

        return link

    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def get_queryset(self, request):
        return super(LogEntryAdmin, self).get_queryset(request).prefetch_related('content_type')
