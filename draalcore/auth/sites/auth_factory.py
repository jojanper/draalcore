#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3rd party user authentication interface."""

# Project imports
from .google_oauth2 import GoogleOAuth2
from .twitter_oauth import TwitterOAuth
from .fb_oauth import FacebookOAuth
from .onedrive_oauth2 import OneDriveOAuth2


class AuthFactory(object):
    classes = {
        'google': GoogleOAuth2,
        'twitter': TwitterOAuth,
        'facebook': FacebookOAuth,
        'onedrive': OneDriveOAuth2
    }

    @classmethod
    def create(cls, name):
        target_cls = cls.classes.get(name, None)
        return target_cls() if target_cls else None
