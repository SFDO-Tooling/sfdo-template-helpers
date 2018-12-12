from django.db import models

from sfdo_template_helpers.fields import MarkdownField


class Markdowner(models.Model):
    description = MarkdownField(null=True)
