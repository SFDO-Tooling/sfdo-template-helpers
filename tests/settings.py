# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "a secret key for testing"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "sfdo_template_helpers",
    "tests",
]

SITE_ID = 1

MIDDLEWARE = ()

# A one-off key made to run tests. Obviously do not use the key in the test app for
# anything real!
DB_ENCRYPTION_KEY = "SL1lkCS2pFOafsDIdwnypnIL1F0TTMuO_LAULCP6-Xk="
