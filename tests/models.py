from django.db import models

from sfdo_template_helpers.fields import (
    MarkdownField,
    StringField,
)
from sfdo_template_helpers.slugs import AbstractSlug, SlugMixin


class Markdowner(models.Model):
    description = MarkdownField(null=True)
    unsafe_description = MarkdownField(
        null=True,
        is_safe=False,
        allowed_tags=["p", "object"],
        allowed_attrs={"object": ["title", "src"]},
    )
    name = StringField(null=True, blank=True)


class FooSlug(AbstractSlug):
    parent = models.ForeignKey(
        "Foo", on_delete=models.PROTECT, related_name="slugs"
    )


class Foo(SlugMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug_class = FooSlug
