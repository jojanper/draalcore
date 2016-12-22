#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Code locking using model based approach"""

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

# System imports
import os
import json
from django.db.models import Q
from django.conf import settings
from django.db import models, IntegrityError


DEFAULT_LOCK = 'lock1'


class Lock(object):
    def __init__(self, instance, unique_id):
        self.instance = instance
        self.id = unique_id
        self.next_id = self.id + 1

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self.instance, self.id)

    @property
    def unique_id(self):
        return self.id

    def save(self):
        self.instance.run_id = self.next_id
        self.instance.save()


class CodeLockManager(models.Manager):
    """Model manager for code locking"""

    def acquire_lock(self, lock_id=DEFAULT_LOCK):
        item = self.select_for_update().get(lock_id=lock_id)
        return Lock(item, item.run_id)

    def release_lock(self, lock):
        lock.save()


class CodeLock(models.Model):
    """Model for storing media related jobs"""

    lock_id = models.CharField(max_length=90, blank=True, null=True)
    run_id = models.BigIntegerField(default=0)

    objects = CodeLockManager()

    class Meta:
        db_table = 'codelock'

    def __unicode__(self):
        return "%s (%s)" % (self.__class__.__name__, self.lock_id)


class MutexHandler(object):
    def __init__(self, locker):
        self._locker = locker

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._locker)

    def acquire(self, lock_id=DEFAULT_LOCK):
        return self._locker.acquire_lock(lock_id)

    def release(self, lock):
        self._locker.release_lock(lock)


#
# Code lockers
#
lock_factory = MutexHandler(CodeLock.objects)
