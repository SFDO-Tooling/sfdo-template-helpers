=============================
SFDO Template Helpers
=============================

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

    pip install -e git+https://github.com/SFDO-Tooling/sfdo-template-helpers.git@v0.1.0#egg=sfdo_template_helpers

Or install the development HEAD::

    pip install -e git+https://github.com/SFDO-Tooling/sfdo-template-helpers.git@master#egg=sfdo_template_helpers

`sfdo-template-helpers` is not distributed on PyPI.

Features
--------

* MarkdownField - A Django-ORM TextField that stores Markdown formatted text and makes it available as rendered (and properly bleached/whitelisted) HTML.

Documentation
-------------

MarkdownField
'''''''''''''

You can use MarkdownField like an ordinary TextField::

    class Product(models.Model):
        description = MarkdownField(max_length=2000, null=True, blank=True, help_text='Displayed on the product summary.')

The field does no validation that it is indeed Markdown formatted text, but instead adds a lazy property to the model instance, which will render the text as HTML. The rendered HTML has been ``mark_safe``'d for Django templates.

It has one additional kwarg, ``property_suffix`` that defaults to ``_html``. This is the ... suffix of the property that will be added to your model. Our earlier field would be rendered at ``product.description_html``.

Rendering is safe by default and limited to a SFDC ProdSec reviewed list of properties and attributes. To override what HTML is whitelisted, subclass MarkdownField and override ``markdown_tags`` and ``markdown_attrs``. WARNING: the output of the html property will *still* be a SafeString.


Running Tests
-------------

With py.test::

    $ workon sfdo-template-helpers
    (sfdo-template-helpers) $ export DJANGO_SETTINGS_MODULE=tests.settings
    (sfdo-template-helpers) $ pytest

Using tox to run multiple versions::

    $ workon sfdo-template-helpers
    (sfdo-template-helpers) $ poetry install
    (sfdo-template-helpers) $ tox

Publishing releases
-------------------

Bump the version number in ``sfdo_template_helpers/__init__.py``, and
make a tagged commit. Then::

    $ workon sfdo-template-helpers
    (sfdo-template-helpers) $ git push origin --tags
    (sfdo-template-helpers) $ poetry publish --build
