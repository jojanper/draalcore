#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cache interface and base classes"""

# System imports
from abc import ABCMeta
from django.core.cache import cache


__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2015"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"


class DataCache(object):
    """Cache interface for fetching and resetting cache data

    Attributes
    ----------
    cache_disable - Enable or disable use of cache
    """

    # Set to True to disable caching
    cache_disable = False

    def __init__(self, cache_key, callback=None, cache_reset=False,
                 timeout=2592000, cache_backend=cache):
        """
        Parameters
        ----------
        cache_key : string
            Cache key
        callback : function
            Callback function (to be called) in case cache hit miss occurs
        cache_reset : boolean
            True if cache data is to be renewed, False otherwise
        timeout : integer
            Number of seconds the data should be stored in the cache (default: 30 days)
        cache_backend : object
            Cache backend implementation
        """
        self._cache_key = cache_key.replace(' ', '')
        self._cache_reset = cache_reset | self.cache_disable
        self._callback = callback
        self._timeout = timeout
        self._cache_backend = cache_backend

    def fetch(self, **kwargs):
        """Fetch data from cache and in case data is not available, add data to cache
        and then return it.

        Parameters
        ----------
        kwargs
           Keyworded arguments for the callback function.

        Returns
        -------
        out : dict
           Requested data (either from cache or from database)
        """
        if self._cache_reset:
            self.delete()

        data = self._cache_backend.get(self._cache_key)
        if data is None:
            data = self._callback(**kwargs)
            self._cache_backend.set(self._cache_key, data, self._timeout)

        return data

    def delete(self):
        """Invalidate specified cache key."""
        self._cache_backend.delete(self._cache_key)


class CacheObject(object):
    """Data caching interface."""

    def __init__(self, cache_key, cache_reset=False, cache_backend=cache):
        """
        Args:
          cache_key (string) : cache key
          cache_reset (bool) : True if cache data is to be renewed, False otherwise
          cache_backend (Object) : Cache backend
        """
        self._cache_key = cache_key
        self._cache_reset = cache_reset
        self._cache_backend = cache_backend

    def cache_obj(self, callback, timeout):
        """Retrieve cache object.

        Args:
            callback (function) : Callback to database method for cache hit miss
            timeout (integer) : Cache key timeout

        Cache object for requesting the data (either from cache or database).
        """
        return DataCache(self._cache_key, callback,
                         cache_reset=self._cache_reset,
                         timeout=timeout)

    def invalidate(self):
        """Invalidates cache object."""
        DataCache(self._cache_key, cache_backend=self._cache_backend).delete()


class CacheBase(object):
    """Base class for data caching"""

    __metaclass__ = ABCMeta

    def __init__(self):
        self._base_key = self.__class__.__name__

    def create_cache_key(self, key_components):
        """Create cache key from key components.

        Args:
          key_components (list) : Data components for cache key

        For example: key_components=['a', 'abc'] -> Key is <key_prefix>_a_abc where
        <key_prefix> is the name of the inherited class.

        Returns the final cache key as list.
        """
        assert isinstance(key_components, list)

        keys = [self._base_key]
        for key in key_components:
            keys.append(key)
        joint_key = '_'.join(str(key) for key in keys)

        return [joint_key]

    def get_cache_keys(self):
        raise NotImplementedError('get_cache_keys() not implemented by ' % (self._base_key))

    def invalidate_cache(self, fn, **kwargs):
        """Invalidate cache keys.

        Args:
          fn (function) : Callback for generating cache keys

        Returns cache keys as list.
        """
        cache_keys = fn(**kwargs)
        for key in cache_keys:
            CacheObject(key).invalidate()

        return cache_keys

    def cache_obj(self, fn, callback, timeout=2592000, cache_reset=False, **kwargs):
        """Returns cache object.

        Args:
          fn (function) : Callback for generating cache keys
          callback (function) : Callback in case of cache hit miss
          cache_reset (bool) : True if cache data is to be renewed, False otherwise
          timeout (integer) : Number of seconds the data should be stored in the cache

        Returns the cache object for the first key. Multiple keys are not supported.
        """
        cache_keys = fn(**kwargs)
        assert len(cache_keys) == 1
        return CacheObject(cache_keys[0], cache_reset).cache_obj(callback, timeout)
