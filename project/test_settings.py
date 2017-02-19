import os  # noqa
import sys  # noqa
from .settings import *  # noqa

USE_CACHING = False
DEBUG = False
TEST_URLS = True

# Select Django's test runner or nose runner
if os.environ.get('DJANGO_TEST_RUNNER', False):
    TEST_RUNNER = 'django.test.runner.DiscoverRunner'
else:
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = ['--with-spec', '--spec-color']
    INSTALLED_APPS += ('django_nose',)  # noqa

# Make tests faster
DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}  # noqa

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

UPLOAD_MEDIA_ROOT = 'build/test_upload/'

# Test ReST API is located here
LOGIN_EXEMPT_URLS += (r'^test-api',)  # noqa

# No application version code checking used for tests
if 'draalcore.middleware.version.ApplicationVersionMiddleware' in MIDDLEWARE_CLASSES:  # noqa
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)  # noqa
    MIDDLEWARE_CLASSES.remove('draalcore.middleware.version.ApplicationVersionMiddleware')

# When you supply None as a value for an app, Django will consider the app as an app without migrations
# regardless of an existing migrations submodule. This can be used, for example, in a test settings file
# to skip migrations while testing (tables will still be created for the apps' models).
if 'test' in sys.argv[1:]:
    MIGRATION_MODULES = {
        'auth': None
    }
