=====================
SFDO Template Helpers
=====================

.. image:: https://badge.fury.io/py/sfdo-template-helpers.svg
    :target: https://badge.fury.io/py/sfdo-template-helpers

.. image:: https://travis-ci.org/SFDO-Tooling/sfdo-template-helpers.svg?branch=master
    :target: https://travis-ci.org/SFDO-Tooling/sfdo-template-helpers

.. image:: https://codecov.io/gh/SFDO-Tooling/sfdo-template-helpers/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/SFDO-Tooling/sfdo-template-helpers

A set of Django helpers and utils used by sfdo-template projects.

Quickstart
----------

Install the current version of SFDO Template Helpers::

    $ pip install -e git+https://github.com/SFDO-Tooling/sfdo-template-helpers.git@v0.1.0#egg=sfdo_template_helpers

Or install the development HEAD::

    $ pip install -e git+https://github.com/SFDO-Tooling/sfdo-template-helpers.git@master#egg=sfdo_template_helpers

`sfdo-template-helpers` is not distributed on PyPI.

Features
--------

* MarkdownField - A Django-ORM TextField that stores Markdown formatted text and makes it available as rendered (and properly bleached/whitelisted) HTML.

Documentation
-------------

MarkdownField
'''''''''''''

You can use MarkdownField like an ordinary TextField:

.. code-block:: python

   class Product(models.Model):
       description = MarkdownField(max_length=2000, null=True, blank=True, help_text='Displayed on the product summary.')

The field does no validation that it is indeed Markdown formatted text, but instead adds a lazy property to the model instance, which will render the text as HTML. The rendered HTML has been ``mark_safe``'d for Django templates.

It has one additional kwarg, ``property_suffix`` that defaults to ``_html``. This is the ... suffix of the property that will be added to your model. Our earlier field would be rendered at ``product.description_html``.

Rendering is safe by default and limited to a SFDC ProdSec reviewed list of properties and attributes. To override what HTML is whitelisted, provide ``allowed_tags`` and ``allowed_attrs`` kwargs when constructing the field. WARNING: the output of the html property will *still* be a SafeString. To leave the string tainted, you may add the `is_safe=False` kwarg.

.. code-block:: python

   class Product(models.Model):
       bad_markdown_for_review = MarkdownField(allowed_attrs={"a": ["href", "alt", "title"]}, is_safe=False)


StringField
'''''''''''

Postgres treats columns defined as text, varchar(50), and varchar(50000) all the same. Stop putting an unnecessary max_limit on your CharField just to get a single line input widget. Use StringField. Feel good.

Admin
'''''

This contains a number of submodules. Those you are most likely to use are ``middleware``, ``serializers``, and ``views``.

``middleware`` contains a middleware class that will restrict a set of views to a set of originating IP addresses. This is intended to limit Admin API views to Salesforce-internal IPs.

``serializers`` and ``views`` contain base classes for automatically generating the classes you need for a DRF API that provides transparent access to all the models linked up. This is suitable for making an Admin API.

Crypto
''''''

This contains two functions, ``fernet_encrypt`` and ``fernet_decrypt``.  They both require a value to be set in the Django project's settings, ``DB_ENCRYPTION_KEY``, which should be kept secret. You can get a valid value for this setting by running the following in a Python shell:

.. code-block:: python

   from cryptography.fernet import Fernet
   Fernet.generate_key()

Addresses
'''''''''

This contains a single function, ``get_remote_ip``, which gets the originating IP of the request from the headers that Heroku sets.

Logfmt
''''''

This provides some utilities for logfmt logs. You can set them up like this:

.. code-block:: python

   LOGGING = {
       "version": 1,
       "disable_existing_loggers": True,
       "filters": {
           "job_id": {"()": "sfdo_template_helpers.logfmt_utils.JobIDFilter"},
       },
       "formatters": {
           "logfmt": {
               "()": "sfdo_template_helpers.logfmt_utils.LogfmtFormatter",
               "format": (
                   "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
               ),
           },
       },
       "handlers": {
           "console": {
               "level": "DEBUG",
               "class": "logging.StreamHandler",
               "filters": ["request_id"],
               "formatter": "logfmt",
           },
       },
       "loggers": {
           "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
       },
   }

Running Tests
-------------

With py.test::

    $ workon sfdo-template-helpers
    (sfdo-template-helpers) $ export DJANGO_SETTINGS_MODULE=tests.settings
    (sfdo-template-helpers) $ pytest

Using tox to run multiple versions::

    $ workon sfdo-template-helpers
    (sfdo-template-helpers) $ pip install -r requirements.txt
    (sfdo-template-helpers) $ tox

Publishing releases
-------------------

Bump the version number in ``sfdo_template_helpers/__init__.py``, and
make a tagged commit. Then::

    $ workon sfdo-template-helpers
    (sfdo-template-helpers) $ git push origin --tags

We publish to GitHub, not to PyPI, yet.
