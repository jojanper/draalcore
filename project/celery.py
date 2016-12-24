from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('draalcore')
app.config_from_object('django.conf:settings')

INSTALLED_APPS = settings.INSTALLED_APPS
app.autodiscover_tasks(lambda: INSTALLED_APPS)
