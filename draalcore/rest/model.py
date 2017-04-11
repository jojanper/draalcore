#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model mapping utilities"""

# System imports
import sys
import inspect
import logging
import importlib
from django.apps import apps
from django.core.urlresolvers import reverse

# Project imports
from draalcore.exceptions import (ModelNotFoundError, ModelAccessDeniedError, ModelSerializerNotDefinedError,
                                  ModelSerializerNotFoundError, AppNotFoundError)


logger = logging.getLogger(__name__)


def locate_base_module(model_cls, postfix='serializers'):
    """Return base path by finding removing everything starting from last occurrence of 'models' in the models path name"""
    path = inspect.getmodule(model_cls).__name__
    return path[:path.rfind('models') - 1] + '.' + postfix


def model_load_error_message(msg_prefix, obj):
    return msg_prefix.format(reverse('rest-api-model', kwargs={
        'app': obj.app_label,
        'model': obj.model_name
    }))


def app_load_error_message(msg_prefix, app):
    return msg_prefix.format(reverse('rest-api-app-actions-listing', kwargs={
        'app': app
    }))


class ModelContainer(object):
    """Interface for accessing application models based on application and model name."""

    def __init__(self, app_label, model_name):
        self._app_label = app_label
        self._model_name = model_name

    @property
    def app_label(self):
        return self._app_label

    @property
    def model_name(self):
        return self._model_name

    @property
    def model_cls(self):
        """
        Return model class that corresponds to current object instance.

        Raises:
        -------
        ModelAccessDeniedError
           Model access is denied via ReST API.
        ModelNotFoundError
           Model was not found.
        """
        for model in apps.get_models():
            if self._app_label == model._meta.app_label and self._model_name == model._meta.db_table:

                # If model's EXTERNAL_API attribute is not True, then access to model is denied
                if not getattr(model, 'EXTERNAL_API', False):
                    raise ModelAccessDeniedError(model_load_error_message('API call {} not allowed', self))

                return model

        raise ModelNotFoundError(model_load_error_message('Invalid API call {}', self))


class ModelsCollection(object):
    """Interface for accessing public application models."""

    @classmethod
    def serialize(cls):
        return [dict(app_label=_cls.app_label, model=_cls.db_table) for _cls in ModelsCollection()]

    def __iter__(self):
        """Model class meta iterator."""
        return iter([model._meta for model in apps.get_models() if getattr(model, 'EXTERNAL_API', False)])


class AppsCollection(object):
    """Interface for accessing public applications."""

    @classmethod
    def serialize(cls, actions_serializer_fn):
        return [dict(app_label=app.display_name, model=None,
                     actions=app.serialize_all_actions(actions_serializer_fn))
                for app in AppsCollection()]

    def __iter__(self):
        """Applications iterator."""
        return iter([app for app in apps.get_app_configs() if getattr(app, 'public_app', False)])

    def get_app(self, app_name):
        """Return application object that corresponds to specified name"""
        for app in AppsCollection():
            if app_name == app.display_name:
                return app

        raise AppNotFoundError(app_load_error_message('Invalid API call {}', app_name))


class SerializerFinder(object):
    """
    Interface for retrieving model serializer classes. Model may define serializer implementation that is
    inherited from BaseSerializerObject or define just the plain serializer class. The former is signaled
    with SERIALIZER_OBJECT attribute and the latter with SERIALIZER attribute. The object takes precedence
    over plain serializer definition in case both are defined for the model.
    """

    def __init__(self, model_cls):
        self._model_cls = model_cls

    @property
    def serializer_module(self):
        """Return serializer module name for the model."""
        return locate_base_module(self._model_cls, 'serializers')

    @property
    def object(self):
        """Return serializer class corresponding to the SERIALIZER_OBJECT attribute."""

        # If attribute is not defined then it's not present
        if not hasattr(self._model_cls, 'SERIALIZER_OBJECT'):
            return None

        try:
            module = self.serializer_module
            loaded_mod = getattr(sys.modules, module, importlib.import_module(module))

            # Make sure the serializer object class is available
            if not hasattr(loaded_mod, self._model_cls.SERIALIZER_OBJECT):
                return None

            # Return the actual serializer object class
            return getattr(loaded_mod, self._model_cls.SERIALIZER_OBJECT)
        except ImportError:
            return None

    @property
    def serializer(self):
        """
        Return serialize class for the specified model class.

        Raises:
        -------
        ModelSerializerNotDefinedError
           Serializer class not defined for the model.
        ModelSerializerNotFoundError
           Error in locating the serializer class.
        """

        # Is serializer attribute present and enabled
        if not hasattr(self._model_cls, 'SERIALIZER'):
            msg = model_load_error_message('No data serializer defined for {}', self._model_cls._meta)
            raise ModelSerializerNotDefinedError(msg)

        # Load the module and import if not yet loaded
        try:
            module = self.serializer_module
            loaded_mod = getattr(sys.modules, module, importlib.import_module(module))

            # Make sure the serializer is available
            if not hasattr(loaded_mod, self._model_cls.SERIALIZER):
                msg = model_load_error_message('Invalid data serializer defined for {}', self._model_cls._meta)
                raise ModelSerializerNotFoundError(msg)

            # Return the actual serializer
            return getattr(loaded_mod, self._model_cls.SERIALIZER)
        except ImportError as e:
            logger.debug(e)
            msg = model_load_error_message('Unable to import serializer class for {}', self._model_cls._meta)
            raise ModelSerializerNotFoundError(msg)
