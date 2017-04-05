#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System imports
from django.conf import settings
from django.core.mail import send_mail


class Mailer(object):

    def __init__(self, subject):
        self._subject = settings.EMAIL_SUBJECT_PREFIX + subject

    def send_message(self, message, recipients, default_from=settings.DEFAULT_FROM_EMAIL):
        send_mail(self._subject, message, default_from, recipients, fail_silently=True)
