#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Library setup, inspired by https://github.com/pypa/sampleproject"""

import json
from setuptools import setup, find_packages


EXCLUDE = ['*tests*', '*test_apps*', 'setup.py', 'node_modules', 'build', 'virtualenv', 'project']

with open('package.json') as json_data:
    APP_VERSION = json.load(json_data)['version']

install_requires = [
    'django>=1.9,<1.10',
    'djangorestframework==3.5.3',
    'six>=1.10.0,<2dev',
    'celery>=3.1.23,<4dev',
    'httplib2>=0.9.2,<1dev',
    'google-api-python-client==1.5.5',
    'oauth2',
    'requests-oauthlib==0.7.0',
    'onedrivesdk==1.1.1',
]

setup(
    name='draalcore',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=APP_VERSION,

    description='Draal core library for Python',
    long_description='Draal core library for Python',

    # The project's main homepage.
    url='https://github.com/jojanper/draalcore',

    # Author details
    author='Juha Ojanpera',
    author_email='juha.ojanpera@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',

        # Pick your license as you wish (should match "license" above)
        'License :: MIT License',

        'Framework :: Django',
        'Framework :: Django :: 1.9',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
    ],

    # What does your project relate to?
    keywords='django ReST application',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=EXCLUDE),

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'draalcore.test_utils': ['audio.mp3', 'pic.gif', 'pic.jpg', 'test.invalid', 'video.mp4', 'test.txt'],
    },

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_requires
)
