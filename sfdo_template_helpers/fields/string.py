from django.db import models


class StringField(models.TextField):
    """ A simple unlimited length string field.

    Django's CharField requires a max_length, and TextField displays a multi-
    line widget, but in Postgres there's no reason to add an arbitrary max
    thanks to the `varlena` storage format. So this is a TextField that
    displays as a single line instead of a multiline TextArea.

    That's all."""

    def formfield(self, **kwargs):
        # skip TextField's override of models.Field.formfield
        return models.Field.formfield(self, **kwargs)
