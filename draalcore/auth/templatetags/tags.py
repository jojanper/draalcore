#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Template tags for registration apps."""

# System imports
from django import template
from django.conf import settings


register = template.Library()


@register.filter(name='social_auth')
def social_auth(user):
    """
    Return True if specified user has logged in with local account, False if user
    uses 3rd party account for sign-in.
    """
    return True if user.password is not settings.SOCIAL_AUTH_USER_PASSWORD else False
