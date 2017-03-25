#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ReST API handlers"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


from draalcore.rest.request_data import RequestData  # noqa
from draalcore.exceptions import AppException  # noqa
from draalcore.rest.response_data import ResponseData  # noqa
from draalcore.rest.mixins import GetMixin, PostMixin, DeleteMixin, PutMixin, PatchMixin  # noqa
from draalcore.rest.auth import RestAuthentication, SessionNoCSRFAuthentication  # noqa
from draalcore.rest.file_upload import FileUploadHandler  # noqa
from draalcore.rest.views import api_response, AppActionsPermission, RestAPIBaseView, RestAPINoAuthView, RestAPIBasicAuthView  # noqa


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generate authentication token for new user"""
    if created:
        Token.objects.create(user=instance)
