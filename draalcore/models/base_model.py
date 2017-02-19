#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base model(s)"""

# System imports
import six
import json
import logging
from copy import copy
from django.utils import timezone
from django.db import models, connection
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION, LogEntry

# Project imports
from draalcore.models.base_manager import BaseManager
from draalcore.middleware.current_user import get_current_user
from draalcore.models.fields import AppModelFieldParser, AppModelCharField

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2014-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

logger = logging.getLogger(__name__)


class ModelFieldDoesNotExist(object):
    pass


class ModelMetaSerializer(object):
    """Interface for serializing model fields data."""

    UI_FIELDS = ['type', 'editable', 'required', 'attributes']

    def __init__(self, model):
        """
        Create class.

        Parameters
        ----------
        model
            Model class for field data serialization.
        """
        self._model = model

    @property
    def model(self):
        """Return model class."""
        return self._model

    def attributes(self, obj):
        """
        Determine field attributes for specified model field object.

        Parameters
        ----------
        obj
           Model field object.

        Returns
        -------
        dict
           Field attributes. Attributes itself are field specific.
        """
        return obj.attributes

    def required(self, obj):
        """
        Determine if field value is required.

        Parameters
        ----------
        obj
           Model field object.

        Returns
        -------
        Boolean
        """
        return obj.mandatory

    def editable(self, obj):
        """
        Determine if field value is editable.

        Parameters
        ----------
        obj
           Model field object.

        Returns
        -------
        Boolean
        """
        return obj.editable

    def type(self, obj):
        """
        Determine field UI type.

        Parameters
        ----------
        obj
           Model field object.

        Returns
        -------
        String
        """
        return obj.field.UI_TYPE

    def additional_attributes(self, obj, data):
        """
        Determine additional meta data attributes for specified model field object.

        Parameters
        ----------
        obj
           Model field object.
        data : dict
           Model metadata.

        Returns
        -------
        dict
           Update metadata for the model.
        """
        if hasattr(obj, 'additional_attributes'):
            data.update(obj.additional_attributes)

        if hasattr(obj, 'recursive'):
            data.update(obj.recursive(ModelMetaSerializer))

        if hasattr(obj, 'label'):
            data.update({'label': obj.label})

        if hasattr(obj, 'help_text'):
            data.update({'help': obj.help_text})

        return data

    @property
    def data(self):
        """
        Determine serialized field data from model.

        Returns
        -------
        out : dict
            Field names and their types as key/value pairs
        """

        meta_data = {}
        parsers = [self.model.field_parser(False), self.model.field_parser(True)]
        for parser in parsers:
            for field in parser:
                if field.ui_field:
                    meta = {}
                    for key in self.UI_FIELDS:
                        meta[key] = getattr(self, key)(field)
                    meta = self.additional_attributes(field, meta)
                    meta_data[field.name] = meta

        return meta_data


class ModelBaseManager(BaseManager):
    pass


class BaseModel(models.Model):
    """Base model for applications to use. Includes only utility methods."""

    # If set to False, model is private, that is, not accessible via ReST API
    EXTERNAL_API = True

    # Model actions that are private, that is, not visible via ReST API
    DISALLOWED_ACTIONS = []

    # Additional fields that should get serialized as part of the model serialization
    ADDITIONAL_SERIALIZE_FIELDS = []

    # Model fields that should not get serialized as part of the model serialization
    DISABLED_SERIALIZE_FIELDS = []

    # Model search field lookups, e.g., ['name__contains']
    SEARCH_FIELDS = []

    # Model fields that can be updated from UI. Empty list indicates all relevant fields.
    # This is used by the model meta serializer.
    PARTIAL_UPDATE_FIELDS_META = []

    # Ordering mapper from input field to model field, this is mainly used with DataTables server side processing.
    # For example, {'name': 'name'} -> input field 'name' maps to model field 'name'.
    SORT_COLUMN_NAME_MAP = None

    # Name of field from serializer output that can be used as display name for the model item
    DISPLAYREF = None

    class Meta:
        abstract = True

    objects = ModelBaseManager()

    @classmethod
    def execute_sql(cls, sql, params):
        """Execute raw SQL."""
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor

    @classmethod
    def serialize_meta(cls):
        """Serialize model fields meta data."""
        return ModelMetaSerializer(cls).data

    @property
    def content_type(self):
        """Return content type for the model."""
        return ContentType.objects.get_for_model(self)

    @classmethod
    def serializer_fields(cls):
        """Return model field names for data serialization."""
        fields = AppModelFieldParser(cls._meta, True).serializer_fields + AppModelFieldParser(cls._meta, False).serializer_fields
        fields = fields + cls.ADDITIONAL_SERIALIZE_FIELDS
        return list(set(fields) - set(cls.DISABLED_SERIALIZE_FIELDS))

    @classmethod
    def field_parser(cls, related_fields_parser=False):
        """Return model's field parser object."""
        return AppModelFieldParser(cls._meta, related_fields_parser)

    @classmethod
    def serialize_list_url(cls):
        """Return URL to model listing."""
        kwargs = {
            'app': cls._meta.app_label,
            'model': cls._meta.db_table
        }
        return reverse('rest-api-model', kwargs=kwargs)

    @classmethod
    def meta_attributes(cls):
        """Return additional (model specific) meta attributes for model meta serialization."""
        return {}


class BaseDetails(BaseModel):
    """Base model with details regarding latest change details (user + timestamp)."""

    # Model visibility status, deleted items are not shown to user
    STATUS_ACTIVE = 'Active'
    STATUS_DELETED = 'Deleted'
    STATUS_PENDING = 'Pending'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, u'Active'),
        (STATUS_DELETED, u'Deleted'),
        (STATUS_PENDING, u'Pending'),
    )
    status = AppModelCharField(private=True, ui_serialize=False, max_length=24, choices=STATUS_CHOICES,
                               default=STATUS_ACTIVE, help_text='Item activity status')

    # Timestamp when data was last modified
    last_modified = models.DateTimeField(auto_now_add=True, help_text='Latest modification timestamp.')

    # Who modified the data last
    modified_by = models.ForeignKey(User, blank=True, null=True, editable=False, help_text='User who modified the data.')

    # Admin will use this as manager
    admin_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        # Who is making the changes
        if 'modified_by' in kwargs:
            self.modified_by = kwargs['modified_by']
            kwargs.pop('modified_by')

        self.last_modified = timezone.now()
        if 'update_fields' in kwargs:
            if 'modified_by' not in kwargs['update_fields']:
                kwargs['update_fields'].append('modified_by')
            kwargs['update_fields'].append('last_modified')

        super(BaseDetails, self).save(*args, **kwargs)

    def deactivate(self):
        """Set model item to non-active status."""
        kwargs = {'status': self.STATUS_DELETED}
        self.set_values(**kwargs)

    def activate(self):
        """Set model item to active status."""
        kwargs = {'status': self.STATUS_ACTIVE}
        self.set_values(**kwargs)


class EventHandlingMixin(object):
    """Write and read model events using Django's LogEntry."""

    def create_related_event(self, field, event_item):
        """Create related event to model history."""

        if isinstance(event_item, list):
            event = {
                field: {
                    'title': 'New values',
                    'data': [str(item) for item in event_item]
                }
            }
            self.create_event(get_current_user(), event)

    def create_event(self, user, events, action=ADDITION):
        """Create change or event message related to model."""
        if not isinstance(events, list):
            events = [events]

        change_history = json.dumps(events)
        content_type = self.content_type
        LogEntry.objects.log_action(user_id=user.id,
                                    content_type_id=content_type.id,
                                    object_id=self.pk,
                                    object_repr=force_text(self),
                                    action_flag=action,
                                    change_message=change_history)

    def get_events(self):
        """Return the model changes/events as queryset."""
        content_type = self.content_type
        query = LogEntry.objects.filter(object_id=self.pk, content_type_id=content_type.id, change_message__gt=0)
        query = query.select_related('user')
        return query.order_by('id').reverse()


class ModelLogger(EventHandlingMixin, BaseDetails):
    """Base class for logging model changes and events."""

    # Fields that are not part of model changes tracking
    EVENT_DISCARDED_FIELDS = ['last_modified', 'modified_by']

    # Fields that are tracked for model changes, by default all fields are tracked
    EVENT_TRACK_FIELDS = []

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):

        editing_user = None
        if 'editing_user' in kwargs:
            editing_user = kwargs['editing_user']
            del kwargs['editing_user']

        super(ModelLogger, self).__init__(*args, **kwargs)

        self.modified_by = editing_user if editing_user else get_current_user()

        self._changed_fields = {}

        self._fields = [field.name for field in self._meta.fields]

    @property
    def changed_fields(self):
        return self._changed_fields

    def is_tracked_field(self, field):
        """Return True if specified field should be event tracked, False otherwise."""
        is_tracked = field in self.EVENT_TRACK_FIELDS if self.EVENT_TRACK_FIELDS else True
        if is_tracked:
            is_tracked = field not in self.EVENT_DISCARDED_FIELDS

        return is_tracked

    def _save_model_changes(self, changed_fields, created=False):
        """Save changes made to model data as separate DB entry."""

        if isinstance(changed_fields, dict):
            # Determine change message for each field that has changed
            changes = {}
            for key, value in six.iteritems(changed_fields):
                if self.is_tracked_field(key):
                    if value is not ModelFieldDoesNotExist:
                        if created:
                            changes[key] = ['Created value ' + force_text(value)]
                        else:
                            changes[key] = [force_text(value), force_text(getattr(self, key))]

            # Save the model changes and reset change object
            if changes:
                self.create_event(self.modified_by, changes)
                self._changed_fields = {}

    def set_values(self, **kwargs):
        """Update model data and save to DB."""

        # Update data
        updated_fields = []
        for field in self._meta.fields:
            if not field.primary_key and field.name in kwargs:
                old_value = getattr(self, field.name, ModelFieldDoesNotExist)
                if old_value != kwargs[field.name]:
                    updated_fields.append(field.name)
                    self._changed_fields[field.name] = copy(old_value)
                    setattr(self, field.name, kwargs[field.name])

        changed_fields = self._changed_fields

        # Save data, if any updates
        if updated_fields:
            save_kwargs = {
                'update_fields': updated_fields,
                'modified_by': self.modified_by
            }
            self.save(**save_kwargs)

        return changed_fields

    def save(self, *args, **kwargs):
        """Save model and associated changes."""

        # Need to know if model is being created or updated
        create_model = False
        if not self.pk:
            create_model = True

        super(ModelLogger, self).save(*args, **kwargs)

        # If object is created for the first time, get the initial change values
        if create_model:
            for field in self._meta.fields:
                self._changed_fields[field.name] = getattr(self, field.name)

        # Finally, save the model changes
        self._save_model_changes(self.changed_fields, create_model)
