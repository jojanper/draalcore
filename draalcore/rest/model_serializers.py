#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data serializers"""

# System imports
import json
import logging
from rest_framework import serializers
from django.contrib.admin.models import LogEntry

# Project imports
from .actions import ActionsSerializer
from .base_serializers import DynamicFieldsModelSerializer


logger = logging.getLogger(__name__)


class ActionsUrlSerializer(DynamicFieldsModelSerializer):
    """Base serializer class for model actions"""

    actions = serializers.SerializerMethodField('field_actions')

    def field_actions(self, obj):
        return ActionsSerializer.serialize_model_id_actions(self.Meta.model, obj.id)


def field_impl(field):
    """
    Provide serialization implementation for specified model field data.

    Parameters
    ----------
    field
       Name of field of the serialization data.
    """
    def set_field(obj):
        return getattr(obj, 'serialize_{}'.format(field))()
    return set_field


class ModelSerializer(ActionsUrlSerializer):
    """
    Base serializer class for application models. Support for BaseDetails model details and actions serialization.
    """

    # Dynamically create custom serializer fields from model configuration
    DYNAMIC_FIELDS_SETUP = True

    def __init__(self, *args, **kwargs):

        if self.DYNAMIC_FIELDS_SETUP:
            # Fields for which serialization method is needed
            fields = list(set(self.Meta.model.ADDITIONAL_SERIALIZE_FIELDS) - set(['actions']))
            for field in fields:
                # Create field serialization method only if not already specified
                if not hasattr(self, field):
                    # Name of serialization method
                    method_name = 'field_{}'.format(field)

                    # Add to serializer fields
                    self._declared_fields[field] = serializers.SerializerMethodField(method_name)

                    # Provide implementation
                    setattr(self, method_name, field_impl(field))

        # Instantiate the superclass normally
        super(ModelSerializer, self).__init__(*args, **kwargs)

    modified_by = serializers.SerializerMethodField('field_modified_by')
    last_modified = serializers.SerializerMethodField('field_last_modified')

    def field_modified_by(self, obj):
        user = obj.modified_by
        return user.first_name + ' ' + user.last_name if user.first_name else user.username

    def field_last_modified(self, obj):
        return str(obj.last_modified)


class HistorySerializer(ModelSerializer):
    """
    Serialize model change history. The data consists of 'events', 'last_modified',
    and 'modified_by' fields. The first one is list of strings or dicts describing
    the fields that have changed, the second one is the timestamp when change
    occured and the last one describes the user responsible of the change or
    event message.
    """

    DYNAMIC_FIELDS_SETUP = False

    events = serializers.SerializerMethodField("field_events")
    last_modified = serializers.SerializerMethodField("field_last_modified")

    class Meta:
        depth = 1
        model = LogEntry
        fields = ['modified_by', 'last_modified', 'events']

    def field_modified_by(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name if obj.user.first_name else obj.user.username

    def field_last_modified(self, obj):
        return obj.action_time

    def field_events(self, obj):
        try:
            return json.loads(obj.change_message)
        except ValueError:
            return obj.change_message
