#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST actions handlers."""

# System imports
import sys
import logging
import importlib
from django.db import models
from django.conf import settings
from django.db.models.query import QuerySet
from abc import ABCMeta, abstractmethod
from django.core.urlresolvers import reverse

# Project imports
from .handlers import PostMixin, GetMixin, RestAPIBasicAuthView
from .request_data import RequestData
from .response_data import ResponseData
from .serializer_object import SerializerModelDataObject
from draalcore.rest.model import ModelContainer, locate_base_module, ModelsCollection, AppsCollection
from draalcore.exceptions import DataParsingError
from draalcore.middleware.current_user import get_current_request


logger = logging.getLogger(__name__)


def get_module(module):
    """Return specified python module"""
    return getattr(sys.modules, module, importlib.import_module(module))


class BaseAction(object):
    """
    Base class for action execution.

    Attributes:
    -----------
    ACTION
       Name of action.
    MODEL
       Model class. This should be defined for all actions that are derived from CreateAction or
       EditAction base action class. It is not needed for CreateAction or EditAction as those
       classes are valid for all models as such. Only if there is a need to override the
       default behavior, custom class implementation is needed.
    ALLOWED_METHODS
       Allowed HTTP methods under which action can be called.
    LINK_ACTION
       True if action URL can be directly called. Useful, for example, for downloading media files.
    """

    ACTION = None
    MODEL = None
    ALLOWED_METHODS = []
    LINK_ACTION = False

    def __init__(self, request_obj, model_cls):
        """
        Parameters:
        -----------
        request_obj: RequestObject
           Request object.
        model_cls: Model
           Model class for the request.
        """
        self._request_obj = request_obj
        self._model_cls = model_cls

    @classmethod
    def create(cls, request_obj):
        return cls(request_obj, cls.MODEL)

    @property
    def request_obj(self):
        return self._request_obj

    @property
    def model_cls(self):
        return self._model_cls


class CreateAction(BaseAction):
    """Create new model item, applicable to all models."""

    ACTION = 'create'
    ALLOWED_METHODS = ['POST']
    DISPLAY_NAME = 'Create'

    def _execute(self):
        """Create new model item."""
        return self.model_cls.objects.create_model(**self.request_obj.data_params)

    def execute(self, *args, **kwargs):
        return self._execute(*args, **kwargs)


class EditAction(BaseAction):
    """Edit existing model item, applicable to all models."""

    ACTION = 'edit'
    ALLOWED_METHODS = ['POST', 'PATCH']

    def _execute(self, model_obj):
        """Edit model item."""
        return self.model_cls.objects.edit_model(model_obj, **self.request_obj.data_params)

    def execute(self):
        try:
            model_obj = self.model_cls.objects.get(id=self.request_obj.kwargs['id'])
        except self.model_cls.DoesNotExist:
            raise DataParsingError('ID {} does not exist'.format(self.request_obj.kwargs['id']))

        return self._execute(model_obj)


class DeleteAction(EditAction):
    """Delete existing model item, applicable to all models."""

    ACTION = 'delete'
    ALLOWED_METHODS = ['POST']
    DISPLAY_NAME = 'Delete'
    LINK_ACTION = True

    def _execute(self, model_obj):
        """Delete model item by changing its visibility status."""
        model_obj.deactivate()
        return None


class AbstractModelGetAction(BaseAction):
    """HTTP GET action for models."""

    ALLOWED_METHODS = ['GET']

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self):
        """Must be defined in the implementing class"""


class AbstractModelItemGetAction(EditAction):
    """HTTP GET action for model item."""

    ACTION = None
    ALLOWED_METHODS = ['GET']

    __metaclass__ = ABCMeta

    @abstractmethod
    def _execute(self, model_obj):
        """Must be defined in the implementing class"""


def get_action_response_data(obj, url_name, resolve_kwargs, method=None):
    """Return serialized action URL data"""
    return {
        'url': '{}{}'.format(settings.SITE_URL, reverse(url_name, kwargs=resolve_kwargs)),
        'display_name': getattr(obj, 'DISPLAY_NAME', obj.ACTION),
        'method': method or obj.ALLOWED_METHODS[0],
        'direct': obj.LINK_ACTION
    }


class ActionMapper(object):
    """Utility wrapper class for model actions."""

    @classmethod
    def serialize_actions(cls, request_obj, model_cls, cls_options, method, resolver, include_link_actions=False):
        """
        Serialize actions available for model or model item.

        Parameters
        ----------
        request_obj
           Request object.
        model_cls
           Model class for the request object.
        cls_options:
           List of action base classes for model and model item based action processing.
        method
           HTTP method.
        resolver
           URL resolver, should contain 'name' and 'kwargs' keys for URL reverse method.
        include_link_actions
           If True, only those model actions are serialized that have LINK_ACTION attribute set to value True.
           Default value is False.

        Returns
        -------
        dict
           Available actions.
        """

        classes = cls.action_classes(request_obj, model_cls, cls_options, method)

        # Is inclusion of all actions required in URL parameters?
        all_actions = request_obj.has_url_param('actions', 'all')

        # Include actions that do not require input parameters
        if not all_actions and include_link_actions:
            classes = [item for item in classes if item.LINK_ACTION]

        data = {}
        for item in classes:
            resolver['kwargs']['action'] = item.ACTION
            data[item.ACTION] = get_action_response_data(item, resolver['name'], resolver['kwargs'], method)

        return data

    @classmethod
    def action_classes(cls, request_obj, model_cls, cls_options, method):
        """
        Return BaseAction inherited action classes for specified model.

        Parameters
        ----------
        request_obj
           Request object.
        model_cls
           Model class for the request object.
        cls_options:
           List of action base classes for model and model item based action processing. If available action
           classes are to be retrieved for model ID, then the second item in the list is used as reference class
           otherwise the fist item in the list is used. All actions that get accepted to the output list must
           have been derived from this reference class.
        method
           HTTP method that each action class within output list should support.

        Returns
        -------
        list
           Action classes for model.
        """

        module = locate_base_module(model_cls, 'actions')
        target_base_cls = cls_options[0] if 'id' not in request_obj.kwargs else cls_options[1]

        try:
            classes = []
            loaded_mod = get_module(module)
            for name, cls in loaded_mod.__dict__.items():
                # Class must be inherited from the target class
                if target_base_cls and isinstance(cls, type) and issubclass(cls, target_base_cls):
                    # Class must not be imported
                    if cls.__module__ != target_base_cls.__module__:
                        # The model must match that of the target
                        if cls.MODEL.__name__ == model_cls.__name__ and method in cls.ALLOWED_METHODS:
                            if cls.ACTION not in getattr(model_cls, 'DISALLOWED_ACTIONS', []):
                                classes.append(cls)
        except ImportError:
            pass

        # Include the base class if it has action name specified
        if target_base_cls and target_base_cls.ACTION and method in target_base_cls.ALLOWED_METHODS:
            if target_base_cls.ACTION not in getattr(model_cls, 'DISALLOWED_ACTIONS', []):
                classes.append(target_base_cls)

        # Include delete action as special action if id present
        if 'id' in request_obj.kwargs and method in DeleteAction.ALLOWED_METHODS:
            if DeleteAction.ACTION not in getattr(model_cls, 'DISALLOWED_ACTIONS', []):
                classes.append(DeleteAction)

        return classes

    @classmethod
    def create(cls, request_obj, model_cls, action, cls_options, method):
        """
        Create BaseAction inherited action object instance for specified request.

        Parameters
        ----------
        request_obj
           Request object.
        model_cls
           Model class for the request object.
        action
           Action name.
        cls_options:
           Action base classes list for model and model item based action processing.
        method
           HTTP method.

        Returns
        -------
        Object
           CreateAction | EditAction instance.

        Raises
        ------
        DataParsingError
           Action not supported.
        """
        # Find action classes for model
        classes = cls.action_classes(request_obj, model_cls, cls_options, method)

        # Now find the correct action class
        for cls_item in classes:
            if action == cls_item.ACTION:
                return cls_item(request_obj, model_cls)

        raise DataParsingError('Action {} not supported for method {}'.format(action, method))


class ModelActionMixin(GetMixin, PostMixin):
    """Actions mixin handling HTTP GET and HTTP POST queries for model related actions."""

    def _get(self, request_obj):
        """Apply HTTP GET action to application model."""
        return self._execute_action(request_obj, [AbstractModelGetAction, AbstractModelItemGetAction], 'GET')

    def _post(self, request_obj):
        """Apply HTTP POST action to application model."""
        return self._execute_action(request_obj, [CreateAction, EditAction], 'POST')

    def _execute_action(self, request_obj, action_cls, method):
        """Execute model action."""

        action = request_obj.kwargs['action']
        model_cls = ModelContainer(request_obj.kwargs['app'], request_obj.kwargs['model']).model_cls

        # Model definition must be valid
        if hasattr(model_cls, 'serializer_fields'):

            ser_obj = SerializerModelDataObject.create(request_obj, model_cls)

            # Locate action class and execute
            action_obj = ActionMapper.create(request_obj, model_cls, action, action_cls, method)
            obj = action_obj.execute()

            # Serialize data as response
            if obj and isinstance(obj, (models.Model, QuerySet)):
                request_obj.set_queryset(obj)
                obj = ser_obj.serialize().data

            return ResponseData(obj)

        msg = "{} action for '{}' is not supported via the API".format(action, request_obj.kwargs['model'])
        return ResponseData(message=msg)


class AppActionMixin(GetMixin, PostMixin):
    """Actions mixin handling HTTP GET and HTTP POST queries for application related actions."""

    def _get(self, request_obj):
        """Apply HTTP GET action to application."""
        return self._execute_action(request_obj, 'GET')

    def _post(self, request_obj):
        """Apply HTTP POST action to application."""
        return self._execute_action(request_obj, 'POST')

    def _execute_action(self, request_obj, method):
        """Execute application level action."""

        # Find application config object
        app = AppsCollection().get_app(request_obj.kwargs['app'])

        # Find the actual action object
        action_obj = app.get_action_obj(request_obj, method)

        # Execute
        obj = action_obj.execute()

        # Serialize returned data if its queryset or model item
        if obj and isinstance(obj, (models.Model, QuerySet)):

            # Queryset model
            model_cls = obj.model

            # Create serializer based on model
            ser_obj = SerializerModelDataObject.create(request_obj, model_cls)
            request_obj.set_queryset(obj)

            # Serialize queryset data
            obj = ser_obj.serialize().data

        return ResponseData(obj)


class ActionsSerializer(object):
    """
    Actions serializer interface. Lists available actions for (app_label, model) tuple. If URL contains
    'actions' parameter with value 'all', then all available actions are listed. By default only HTTP POST
    actions are listed.

    Attributes:
    -----------
    request_obj
       RequestData instance.
    """

    def __init__(self, request_obj):
        self.request_obj = request_obj

    def serialize(self):
        """
        Interface for serializing application and/or model related actions.

        Returns
        -------
        dict
           Action details.
        """
        return self._serialize_model_actions() if 'model' in self.request_obj.kwargs else self._serialize_app_actions()

    def _serialize_app_actions(self):
        """
        Serialize actions that are application related (not tight to any specific model).

        Returns
        -------
        dict
           Keys describe the name of action and corresponding value the details of the action.
        """
        app = AppsCollection().get_app(self.request_obj.kwargs['app'])
        return app.serialize_actions(get_action_response_data)

    def _serialize_model_actions(self):
        """
        Serialize actions that are related to a model.

        Returns
        -------
        dict
           Action details.
        """
        resolver = {
            'name': 'rest-api-model-action',
            'kwargs': {
                'app': self.request_obj.kwargs['app'],
                'model': self.request_obj.kwargs['model']
            }
        }

        get_base_actions = []
        if 'id' in self.request_obj.kwargs:
            resolver['name'] = 'rest-api-model-id-action'
            resolver['kwargs'].update({'id': self.request_obj.kwargs['id']})

            # First item needs to be None as the base class for actions search is based on the
            # second item when model ID is present.
            get_base_actions.append(None)
            get_base_actions.append(AbstractModelItemGetAction)
        else:
            get_base_actions.append(AbstractModelGetAction)

        fn = ActionMapper.serialize_actions
        model_cls = ModelContainer(self.request_obj.kwargs['app'], self.request_obj.kwargs['model']).model_cls

        # List HTTP POST actions by default
        actions = fn(self.request_obj, model_cls, [CreateAction, EditAction], 'POST', resolver)

        # All actions are requested, include also HTTP GET actions
        if self.request_obj.has_url_param('actions', 'all'):
            actions.update(fn(self.request_obj, model_cls, get_base_actions, 'GET', resolver, include_link_actions=True))

        return actions

    @classmethod
    def serialize_model_id_actions(cls, model_cls, model_id):
        """
        Class method to serialize actions for specified model and model ID. Only those actions are serialized
        that require HTTP POST method with no input data and HTTP GET method that have LINK_ACTION set to True.
        This function will be called automatically when model item gets serialized. The purpose is that only
        those actions will be listed that can be called without specifying input data as part of the HTTP call
        (as those allow simple UI side implementation).

        Parameters
        ----------
        model_cls
           Model class.
        model_id
           Model ID.

        Returns
        -------
        dict
           Action details.
        """
        resolver = {
            'kwargs': {
                'app': model_cls._meta.app_label,
                'model': model_cls._meta.db_table,
                'id': model_id
            },
            'name': 'rest-api-model-id-action'
        }
        request_obj = RequestData(get_current_request(), **resolver['kwargs'])

        cls_fn = ActionMapper.serialize_actions

        # HTTP POST actions that require no input data
        base_action_cls = [None, EditAction]
        actions = cls_fn(request_obj, model_cls, base_action_cls, 'POST', resolver, include_link_actions=True)

        # HTTP GET actions
        base_action_cls = [None, AbstractModelItemGetAction]
        actions.update(cls_fn(request_obj, model_cls, base_action_cls, 'GET', resolver, include_link_actions=True))
        return actions


class ActionsListingMixin(GetMixin):
    """Actions mixin handling model's available actions listing."""

    def _get(self, request_obj):
        """Return available actions for the application model."""
        return ResponseData(ActionsSerializer(request_obj).serialize())


class ModelActionHandler(ModelActionMixin, RestAPIBasicAuthView):
    """ReST API entry point for executing application model action"""
    pass


class AppActionHandler(AppActionMixin, RestAPIBasicAuthView):
    """ReST API entry point for executing application level action"""
    pass


class ActionsListingHandler(ActionsListingMixin, RestAPIBasicAuthView):
    """ReST API entry point for listing available actions for application and/or model."""
    pass


class SystemAppsModelsListingHandler(GetMixin, RestAPIBasicAuthView):
    """ReST API entry point for listing application models and associated actions that are accessible."""
    def _get(self, request_obj):
        args = request_obj.args
        kwargs = request_obj.kwargs

        # Publicly available models (that are associated to some applications)
        data = ModelsCollection.serialize()
        for item in data:
            kwargs['app'] = item['app_label']
            kwargs['model'] = item['model']
            obj2 = RequestData(request_obj.request, *args, **kwargs)
            item['actions'] = ActionsSerializer(obj2).serialize()

        # Publicly available apps that have app level actions
        for app in AppsCollection.serialize(get_action_response_data):
            data.append(app)

        # UI only application views but enabled from backend
        if hasattr(settings, 'UI_APPLICATION_MODELS'):
            for item in settings.UI_APPLICATION_MODELS:
                for app, _models in item.iteritems():
                    for model in _models:
                        data.append({'app_label': app, 'model': model['name'], 'actions': []})

        return ResponseData(data)
