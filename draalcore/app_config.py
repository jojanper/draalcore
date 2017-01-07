#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.apps import AppConfig

from draalcore.exceptions import ActionError


class BaseAppConfig(AppConfig):
    """Base application configuration"""

    # Application is public, that is, exposed to API to some extent
    public_app = True

    # Display name for the API calls, this name is used to identify this app in the URL
    display_name = None

    # List of public actions available for this application
    actions = []


    def serialize_actions(self, serializer_fn):
        """
        Serialize application level actions.

        Parameters
        ----------
        serializer_fn
           Serializer implementation for action object.

        Returns
        -------
        dict
           Key describes name of action and value action details.
        """
        data = {}
        for action in self.actions:
            resolve_kwargs = {
                'app': self.display_name,
                'action': action.ACTION
            }
            data[action.ACTION] = serializer_fn(action, 'rest-api-app-action', resolve_kwargs)

        return data

    def get_action_obj(self, request_obj, method):
        action = request_obj.kwargs['action']
        for action_cls in self.actions:
            if action == action_cls.ACTION and method in action_cls.ALLOWED_METHODS:
                return action_cls(request_obj, action_cls.MODEL)

        msg = "{} action for '{}' application using HTTP {} is not supported via the API"\
            .format(action, self.display_name, method.upper())
        raise ActionError(msg)
