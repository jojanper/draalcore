#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Django settings for the test project"""

import os
import sys
import json

__author__ = "Juha Ojanpera"
__copyright__ = "Copyright 2013-2016"
__email__ = "juha.ojanpera@gmail.com"
__status__ = "Development"

# Location of the module
pyFile = os.path.abspath(__file__)
# Remove extension
pyFile = os.path.splitext(pyFile)[0]
# Remove name of the module
pyFile = os.path.dirname(pyFile)
# We are now one level up in the file hierarchy
PROJECT_ROOT = os.path.dirname(pyFile)

# Append 'apps' folder
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'draalcore'))

# Read version information
with open(os.path.join(PROJECT_ROOT, 'package.json')) as json_data:
    APP_VERSION = json.load(json_data)['version']

DEBUG = True
TEST_URLS = False

ADMINS = (
    ('Juha Ojanpera', 'juha.ojanpera@gmail.com'),
)

# Production environment status
PRODUCTION_ENVIRONMENT = False

MANAGERS = ADMINS

#
# A list of strings representing the host/domain names that this Django
# site can serve. This is a security measure to prevent an attacker from
# poisoning caches and password reset emails with links to malicious hosts
# by submitting requests with a fake HTTP Host header, which is possible
# even under many seemingly-safe webserver configurations.
#
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        # Or path to database file if using sqlite3.
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'draalcore.sqlite3',

        # Not used with sqlite3.
        'USER': 'draalcore',

        # Not used with sqlite3.
        'PASSWORD': 'test',

        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '127.0.0.1',

        # Set to empty string for default. Not used with sqlite3.
        'PORT': '5432',
    }
}

#
# The lifetime of a database connection, in seconds.
#
CONN_MAX_AGE = 60

# Full import path of a serializer class to use for serializing session data.
# Included serializers are:
#
#    'django.contrib.sessions.serializers.PickleSerializer'
#    'django.contrib.sessions.serializers.JSONSerializer'
#
# The default switched from PickleSerializer to JSONSerializer in Django 1.6.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Expire the session when the user closes his or her browser
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# Password for 3rd party authenticated users
SOCIAL_AUTH_USER_PASSWORD = '!social_auth'

#
# URLs which can be viewed without authentication
#
LOGIN_EXEMPT_URLS = (
    r'^admin',
    r'^$',  # allow the root to be viewed by all
)

#
# Name of URL where user should be redirected in case user email data is missing
#
USER_EMAIL_REDIRECT = 'settings-view'

# Auto logout delay in seconds
AUTO_LOGOUT_DELAY = 60 * 60  # equivalent to 60 minutes


#
# Django Nginx Memcache settings
#
CACHE_NGINX = True
CACHE_NGINX_TIME = 3600 * 24  # 1 day, in seconds
# Default backend to use from settings.CACHES
# May need to update the nginx conf if this is changed
CACHE_NGINX_ALIAS = 'default'

#
# Take Celery into use
#
# Add new vhosts: 'sudo rabbitmqctl add_vhost draal_devel'
# Permissions: 'sudo rabbitmqctl set_permissions -p draal_devel guest ".*" ".*" ".*"'
#
BROKER_URL = 'amqp://guest:guest@localhost:5672/draal_devel'

# The default value for the Task.send_error_emails attribute, which if set to
# True means errors occurring during task execution will be sent to ADMINS by email.
CELERY_SEND_TASK_ERROR_EMAILS = True

# Disabling rate limits altogether is recommended if you don’t have any tasks using them.
# This is because the rate limit subsystem introduces quite a lot of complexity.
CELERY_DISABLE_RATE_LIMITS = True

# By default any previously configured handlers on the root logger will be removed.
# If you want to customize your own logging handlers, then you can disable this
# behavior by setting CELERYD_HIJACK_ROOT_LOGGER = False.
CELERYD_HIJACK_ROOT_LOGGER = False


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = PROJECT_ROOT
X_ACCEL_REDIRECT = '/protected/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http:/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'mctqf=#a+#o3h4w&amp;v5hol510+w@u_(mkm-+j=cxkd@r2_^v2&amp;8'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Draal middleware actions
    'draalcore.middleware.login.AutoLogout',
    'draalcore.middleware.login.LoginRequiredMiddleware',
    'draalcore.middleware.login.UserEmailRequiredMiddleware',
    'draalcore.middleware.nginx_memcache.NginxMemcachedCookieUpdate',
    'draalcore.middleware.current_user.CurrentUserMiddleware',
    'draalcore.middleware.version.ApplicationVersionMiddleware',
)

ROOT_URLCONF = 'test.urls'

# List of callables that know how to import templates from various sources.
LOCAL_TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

# A list containing the settings for all template engines to be used with Django.
# Each item of the list is a dictionary containing the options for an individual engine.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],

        'OPTIONS': {

            # A tuple of callables that are used to populate the context in RequestContext.
            # These callables take a request object as their argument and return a dictionary
            # of items to be merged into the context.
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.contrib.messages.context_processors.messages'
            ],
            'debug': DEBUG,

            # List of callables that know how to import templates from various sources.
            'loaders': LOCAL_TEMPLATE_LOADERS
        }
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

#
# The apps
#
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Uncomment the next line to enable the admin:
    'django.contrib.admin',

    'rest_framework',
    'rest_framework.authtoken',
    'nginx_memcache',

    'draalcore',
    'draalcore.models',
    'draalcore.test_models'
)

from .ui_applications import *  # noqa
from local_settings import *  # noqa
