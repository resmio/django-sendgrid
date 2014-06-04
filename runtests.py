#!/usr/bin/env python
import sys
import os

import django
from django.conf import settings


if not settings.configured:
    # Choose database for settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }

    test_db = os.environ.get('DB', 'sqlite')

    if test_db == 'mysql':
        DATABASES['default'].update({
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'sendgrid',
            'USER': 'root',
        })
    elif test_db == 'postgres':
        DATABASES['default'].update({
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'USER': 'postgres',
            'NAME': 'sendgrid',
            'OPTIONS': {
                'autocommit': True,
            }
        })

    settings.configure(
        DATABASES=DATABASES,
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'sendgrid',
        ),
        SITE_ID=1,
        SECRET_KEY='this-is-just-for-tests-so-not-that-secret',
        ROOT_URLCONF='sendgrid.urls'
    )


from django.test.utils import get_runner


def run_tests():
    if hasattr(django, 'setup'):
        django.setup()
    apps = sys.argv[1:] or ['sendgrid', ]
    test_runner = get_runner(settings)
    test_runner = test_runner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(apps)
    sys.exit(failures)


if __name__ == '__main__':
    run_tests()
