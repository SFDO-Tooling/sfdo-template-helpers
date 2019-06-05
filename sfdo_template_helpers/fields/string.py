from django.db import models
from django.contrib.admin import widgets


class StringField(models.TextField):
    """ A simple unlimited length string field.

    Django's CharField requires a max_length, and TextField displays a multi-
    line widget, but in Postgres there's no reason to add an arbitrary max
    thanks to the `varlena` storage format. So this is a TextField that
    displays as a single line instead of a multiline TextArea.

    That's all."""


# Make sure StringField has its own mapping in FORMFIELD_FOR_DBFIELD_DEFAULTS
# so that it takes precedence over its base class TextField.
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
FORMFIELD_FOR_DBFIELD_DEFAULTS[StringField] = {'widget': widgets.AdminTextInputWidget}
