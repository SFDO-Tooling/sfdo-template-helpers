from django.db import models

from sfdo_template_helpers.fields import MarkdownField
from sfdo_template_helpers.fields import StringField


class Markdowner(models.Model):
    description = MarkdownField(null=True)
    unsafe_description = MarkdownField(
        null=True,
        is_safe=False,
        allowed_tags=["p", "object"],
        allowed_attrs={"object": ["title", "src"]},
    )
    name = StringField(null=True, blank=True)
