#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Custom model fields"""

# System imports
import six
import inspect
import logging
from itertools import chain
from django.db import models
from django.db.migrations import Migration
from django.db.models import ForeignKey

# Project imports
from draalcore.exceptions import DataParsingError

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2014-2015,2012"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

logger = logging.getLogger(__name__)


def get_related_model(field):
    """
    Get related model from a model's field instance. If model field is, for example,
    foreign key, then return the model the field is referencing, that is,
    the related model.

    Parameters
    ----------
    field
       Field instance of a model.

    Returns
    -------
    Object
       Model of the field instance.
    """
    return field.remote_field.model


class AppFieldMixin(object):
    """
    Field handling for models that require custom field attributes.

    Attributes:
    -----------
    SUPPORTED_ATTRIBUTES
       Additional attributes supported.
    """

    """
    mandatory: Value must be present
    optional: Value not required
    private: Value is private, not editable via API
    ui_serialize: Serialization status for the field value towards UI
    type: Value type
    label: Verbose name of the field
    """
    SUPPORTED_ATTRIBUTES = ['mandatory', 'optional', 'private', 'ui_serialize', 'type', 'label', 'read_only']

    def __init__(self, *args, **kwargs):
        self._attributes = {}
        for attr in self.SUPPORTED_ATTRIBUTES:
            if attr in kwargs:
                self._attributes[attr] = kwargs[attr]
                del kwargs[attr]

        # Make sure the editing status is set when custom field is used for a model
        if not any([item in self._attributes for item in self.SUPPORTED_ATTRIBUTES[0:4]]):
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)

            # Use the parent if class constructor seems to be the caller
            caller = calframe[1][3] if calframe[1][3] != '__init__' else calframe[2][3]

            if str(caller) not in [Migration.__name__, 'clone']:
                raise Exception('Field editing statuses are missing for %s; called from %s' % (self.__class__.__name__, caller))

        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name in self._attributes:
            return self._attributes[name]

        return super().__getattr__(name)

    @property
    def attributes(self):
        return {}


class BaseFieldType(object):
    """
    Base class for validating custom field data.

    Attributes
    ----------
    type
       Type for the field data.
    description
       Textual description of type for error messages.
    """
    type = None
    type_description = ''

    @classmethod
    def validate_type(cls, name, value, field_obj):
        """
        Validate field value.

        Parameters
        ----------
        name
           Field name
        value
           Field value
        field_obj
           Model field object

        Raises
        ------
        DataParsingError
           Data does not match the required type.
        """
        if not field_obj.null and value is None:
            msg = "Data field '%s' must be of type %s, null is not allowed" % (name, cls.type_description)
            raise DataParsingError(msg)

        elif value and not isinstance(value, cls.type):
            msg = "Data field '%s' must be of type %s" % (name, cls.type_description)
            raise DataParsingError(msg)


class StringFieldType(BaseFieldType):
    """Field data should be string."""
    type = six.string_types
    type_description = 'string'


class IntegerFieldType(BaseFieldType):
    """Field data should be integer"""
    type = int
    type_description = 'integer'


class IntegerListFieldType(BaseFieldType):
    """Field data should be list of integers."""
    type = list
    type_description = 'list of integers'

    @classmethod
    def validate_type(cls, name, value, field_obj):

        # Field value must be list
        super(IntegerListFieldType, cls).validate_type(name, value, field_obj)

        # Each list item must be integer
        if value:
            for item in value:
                if not isinstance(item, int):
                    msg = "Data field '%s' must be of type %s" % (name, cls.type_description)
                    raise DataParsingError(msg)


class Nullable(object):
    null = True


class NotNullable(Nullable):
    null = False


class AppModelTextField(AppFieldMixin, models.TextField):
    """TextField for models."""

    UI_TYPE = 'textarea'

    def __init__(self, *args, **kwargs):
        kwargs['type'] = StringFieldType
        super(AppModelTextField, self).__init__(*args, **kwargs)


class AppModelCharField(AppFieldMixin, models.CharField):
    """CharField for models."""

    UI_TYPE = 'text'

    def __init__(self, *args, **kwargs):
        kwargs['type'] = StringFieldType
        super(AppModelCharField, self).__init__(*args, **kwargs)

    @property
    def attributes(self):
        attr = {}
        for key in ['max_length', 'min_length']:
            attr[key] = getattr(self, key, 0)

        return attr


class ForeignKeyFieldMixin(AppFieldMixin):
    @property
    def attributes(self):
        model = get_related_model(self)
        return {'model': model._meta.db_table}

    @property
    def additional_attributes(self):
        model = get_related_model(self)
        data = {
            'selector': {
                # From which URL to find the selection items
                'url': model.serialize_list_url(),

                # Which field to use when displaying the data item
                'displayKey': model.DISPLAYREF
            }
        }
        data['selector'].update(model.meta_attributes())
        return data


class AppModelForeignKey(ForeignKeyFieldMixin, models.ForeignKey):
    """Foreign key for models."""

    UI_TYPE = 'selector'

    def __init__(self, *args, **kwargs):
        kwargs['type'] = IntegerFieldType
        super(AppModelForeignKey, self).__init__(*args, **kwargs)


class AppModelForeignObjectKey(AppModelForeignKey):
    """Foreign object key for models."""

    UI_TYPE = 'object'

    def recursive(self, serializer_cls):
        model = get_related_model(self)
        meta_data = serializer_cls(model).data
        return {
            '$order': meta_data.keys(),
            '$types': meta_data
        }

    @property
    def additional_attributes(self):
        return {}


class AppModelManyToManyField(ForeignKeyFieldMixin, models.ManyToManyField):
    """ManyToManyField for models."""

    UI_TYPE = 'multiSelector'

    def __init__(self, *args, **kwargs):
        kwargs['type'] = IntegerListFieldType
        super(AppModelManyToManyField, self).__init__(*args, **kwargs)


class AppModelFieldItem(object):
    """Wrapper class for accessing model field attributes."""

    def __init__(self, meta, field, name_map, related_model):
        self._meta = meta
        self._field = field
        self._name_map = name_map
        self._related_model = related_model

    @property
    def field(self):
        return self._field

    @property
    def mandatory(self):
        value = not getattr(self.field, 'primary_key', False) and getattr(self.field, 'mandatory', False)
        return value is True

    @property
    def editable(self):
        # Is read_only attribute set?
        status = not getattr(self.field, 'read_only', False)

        # If field is editable from attribute perspective, check if field name is included in list
        # that describes fields for meta serializer. If there are items in that list, check that
        # field name is included there. If not, mark field as non-editable.
        if status:
            if hasattr(self.model, 'PARTIAL_UPDATE_FIELDS_META') and self.model.PARTIAL_UPDATE_FIELDS_META:
                status = status if self.field.name in self.model.PARTIAL_UPDATE_FIELDS_META else False

        return status

    @property
    def type(self):
        return getattr(self.field, 'type', None)

    @property
    def optional(self):
        return getattr(self.field, 'optional', False) is True

    @property
    def ui_field(self):
        return self.mandatory or self.optional

    @property
    def related_model(self):
        return get_related_model(self.model._meta.get_field(self.field.name))

    @property
    def fk(self):
        cls = self._name_map[self.field.name].__class__
        return True if cls in [ForeignKey, AppModelForeignKey, AppModelForeignObjectKey] else False

    @property
    def related(self):
        return self._related_model

    @property
    def serialize(self):
        return getattr(self.field, 'ui_serialize', True) is True

    def __getattr__(self, name):
        return getattr(self.field, name)

    def validate_type(self, name, value):
        return self.type.validate_type(name, value, self)


class AppModelFieldParser(object):
    """Field parser for application models."""

    def __init__(self, model_meta, related_fields_parser=False):
        """
        Parameters
        ----------
        model_meta
           Model's meta object.
        related_fields_parser
           True if model's related fields are parsed, False for non-related model fields.
        """
        self._model_meta = model_meta
        self._related_fields_parser = related_fields_parser

    def __iter__(self):
        name_map = {item.name: item for item in self._model_meta.get_fields()}
        fields = self._model_meta.fields if not self._related_fields_parser else self._model_meta.many_to_many
        return iter([AppModelFieldItem(self._model_meta, item, name_map, self._related_fields_parser) for item in fields])

    @property
    def serializer_fields(self):
        mode = 'many_to_many' if self._related_fields_parser else 'fields'
        field_objs = [AppModelFieldItem(self._model_meta, field, None, False) for field in getattr(self._model_meta, mode)]
        return [obj.name for obj in field_objs if obj.serialize or obj.primary_key]


class AppModelFieldParserIterator(object):
    """Iterator wrapper for accessing both non-related and related model fields."""

    @classmethod
    def generator(cls, model_meta, related_parser):
        for field in AppModelFieldParser(model_meta, related_parser):
            yield field

    @classmethod
    def create(cls, model_meta):
        """
        Create iterator for model fields.

        Parameters
        ----------
        model_meta
           Model's meta class.

        Returns
        -------
        iterator
           Iterator containing model's non-related and related field objects.
        """
        return chain(cls.generator(model_meta, False), cls.generator(model_meta, True))
