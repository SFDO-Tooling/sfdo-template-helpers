from django.db import models

from sfdo_template_helpers.fields import MarkdownField
from sfdo_template_helpers.fields import StringField


class Markdowner(models.Model):
    description = MarkdownField(null=True)
    name = StringField(null=True, blank=True)
