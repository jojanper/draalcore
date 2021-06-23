#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.apps import AppConfig

from draalcore.exceptions import ActionError


class BaseAppConfig(AppConfig):
    """Base application configuration"""

    # Django to select a configuration class automatically.
    # App config using this should enable this.
    default = False

    # Application is public, that is, exposed to API to some extent
    public_app = True

    # Display name for the apps related API calls, this name is used to identify this app in the URL.
    # Model related actions use the app_label from Meta as display name.
    # The API calls here are not attached to any model.
    display_name = None

    # List of public actions (authentication required) available for this application
    actions = []

    # List of public actions (no authentication required) available for this application
    noauth_actions = []

    def serialize_all_actions(self, serializer_fn):
        """
        Serialize application level actions with and without authentication requirement.

        Parameters
        ----------
        serializer_fn
           Serializer implementation for action object.

        Returns
        -------
        dict
           Key describes name of action and value action details.
        """
        data = self.serialize_actions(serializer_fn, False)
        data.update(self.serialize_actions(serializer_fn, True))
        return data

    def serialize_actions(self, serializer_fn, noauth=False):
        """
        Serialize application level actions.

        Parameters
        ----------
        serializer_fn
           Serializer implementation for action object.
        noauth
           True if actions requiring authentication are to be serialized, False otherwise.

        Returns
        -------
        dict
           Key describes name of action and value action details.
        """
        if noauth:
            actions = self.noauth_actions
            name = 'rest-api-app-public-action'
        else:
            actions = self.actions
            name = 'rest-api-app-action'

        data = {}
        for action in actions:
            resolve_kwargs = {
                'app': self.display_name,
                'action': action.ACTION
            }
            data[action.ACTION] = serializer_fn(action, name, resolve_kwargs)
            data[action.ACTION].update({'authenticate': not noauth})

        return data

    def get_action_obj(self, request_obj, method):
        action = request_obj.kwargs['action']
        noauth = request_obj.kwargs.get('noauth', False)
        actions = self.noauth_actions if noauth else self.actions
        for action_cls in actions:
            if action_cls.match_action(action) and method in action_cls.ALLOWED_METHODS:
                return action_cls(request_obj, action_cls.MODEL)

        msg = "{} action for '{}' application using HTTP {} is not supported via the API"\
            .format(action, self.display_name, method.upper())
        raise ActionError(msg)
