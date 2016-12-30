#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for 3rd party sign-in."""

# System imports
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login


class Base3rdPartyAuth(object):
    PROVIDER = None

    def get_login_page(self):
        return reverse('auth-login')

    def get_callback_url(self):
        return '{}{}'.format(settings.SITE_URL, reverse('oauth2-callback', kwargs={'provider': self.PROVIDER}))

    def get_redirect_url(self, request):
        return request.GET.get('next', '')

    def authenticate(self, request, **kwargs):
        user = authenticate(**kwargs)
        login(request, user)
        return user
