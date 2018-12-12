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

Documentation
-------------

The full documentation is at https://sfdo-template-helpers.readthedocs.io.

Quickstart
----------

Install SFDO Template Helpers::

    pip install sfdo-template-helpers

Features
--------

* TODO

Running Tests
-------------

::

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
