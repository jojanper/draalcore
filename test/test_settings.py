import sys
from settings import *


USE_CACHING = False
DEBUG = False
TEST_URLS = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Make tests faster
DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

UPLOAD_MEDIA_ROOT = 'build/test_upload/'

# Test ReST API is located here
LOGIN_EXEMPT_URLS += (r'^test-api',)

# No application version code checking used for tests
if 'draalcore.middleware.version.ApplicationVersionMiddleware' in MIDDLEWARE_CLASSES:
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES.remove('draalcore.middleware.version.ApplicationVersionMiddleware')

# When you supply None as a value for an app, Django will consider the app as an app without migrations
# regardless of an existing migrations submodule. This can be used, for example, in a test settings file
# to skip migrations while testing (tables will still be created for the apps' models).
if 'test' in sys.argv[1:]:
    MIGRATION_MODULES = {
    }
