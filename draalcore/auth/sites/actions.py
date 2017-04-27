#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3rd party authentication actions"""

# System imports
import logging
from django.http import HttpResponseRedirect

# Project imports
from draalcore.auth.sites.auth_factory import AuthFactory
from draalcore.rest.actions import AbstractModelGetAction


logger = logging.getLogger(__name__)


class ExtAuthAction(AbstractModelGetAction):
    LINK_ACTION = True
    PROVIDER = None

    def execute(self):
        obj = AuthFactory.create(self.PROVIDER)
        url = obj.get_authorize_url(self.request_obj.request)
        return HttpResponseRedirect(url)


class GoogleExtAuthAction(ExtAuthAction):
    ACTION = 'ext-auth-google'
    DISPLAY_NAME = 'Google authentication'
    PROVIDER = 'google'


class FacebookExtAuthAction(ExtAuthAction):
    ACTION = 'ext-auth-facebook'
    DISPLAY_NAME = 'Facebook authentication'
    PROVIDER = 'facebook'


class TwitterExtAuthAction(ExtAuthAction):
    ACTION = 'ext-auth-twitter'
    DISPLAY_NAME = 'Twitter authentication'
    PROVIDER = 'twitter'


class OneDriveExtAuthAction(ExtAuthAction):
    ACTION = 'ext-auth-onedrive'
    DISPLAY_NAME = 'OneDrive authentication'
    PROVIDER = 'onedrive'


class ExtAuthCallbackAction(AbstractModelGetAction):
    LINK_ACTION = True
    PROVIDER = None

    def execute(self):
        obj = AuthFactory.create(self.PROVIDER)
        user = obj.authorize(self.request_obj.request)
        return self.serialize_user(user, auth_data=True)


class GoogleExtAuthCallbackAction(ExtAuthCallbackAction):
    ACTION = 'callback-google'
    DISPLAY_NAME = 'Google authentication callback'
    PROVIDER = 'google'


class FacebookExtAuthCallbackAction(ExtAuthCallbackAction):
    ACTION = 'callback-facebook'
    DISPLAY_NAME = 'Facebook authentication callback'
    PROVIDER = 'facebook'


class TwitterExtAuthCallbackAction(ExtAuthCallbackAction):
    ACTION = 'callback-twitter'
    DISPLAY_NAME = 'Twitter authentication callback'
    PROVIDER = 'twitter'


class OneDriveExtAuthCallbackAction(ExtAuthCallbackAction):
    ACTION = 'callback-onedrive'
    DISPLAY_NAME = 'OneDrive authentication callback'
    PROVIDER = 'onedrive'
