#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base serializers for ReST and more"""

# System imports
from rest_framework import serializers
from django.contrib.auth.models import User


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.

    See http://django-rest-framework.org/api-guide/serializers
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserModelSerializer(DynamicFieldsModelSerializer):
    """Serialize user details"""

    display = serializers.SerializerMethodField('field_display')

    class Meta:
        depth = 1
        model = User
        fields = ['id', 'display', 'email']

    def field_display(self, obj):
        return obj.username
