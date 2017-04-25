#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for 3rd party sign-in."""

# System imports
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login


class Base3rdPartyAuth(object):
    PROVIDER = None

    def get_login_page(self):
        return reverse('auth-login')

    def get_callback_url(self):
        action = 'callback-{}'.format(self.PROVIDER)
        return reverse('rest-api-app-public-action', kwargs={'app': 'auth', 'action': action})

    def get_redirect_url(self, request):
        return request.GET.get('next', '')

    def authenticate(self, request, **kwargs):
        user = authenticate(**kwargs)
        login(request, user)
        return user
