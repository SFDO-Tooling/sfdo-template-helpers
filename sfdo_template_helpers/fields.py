"""
CleanMarkdownField

A subclass of TextField that's designed to support bleached/html safe
rendering with `bleach` and `markdown`.  When used in a model,
`fieldname_html` renders the safe html.

TODO: non-inheritance based customization of the whitelist
TODO: field property to define if its safe or nah
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

import bleach
from markdown import markdown

DEFAULT_SUFFIX = "_html"


class MarkdownDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError("Can only be accessed via an instance.")
        raw_md = instance.__dict__[self.field.name]
        if raw_md is None:
            return ""
        return mark_safe(
            bleach.clean(
                markdown(raw_md),
                tags=self.field.markdown_tags,
                attributes=self.field.markdown_attrs,
            )
        )

    def __set__(self, obj, value):
        raise AttributeError("Read-only Attribute.")


class MarkdownFieldMixin:
    markdown_tags = [
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "b",
        "i",
        "strong",
        "em",
        "tt",
        "p",
        "br",
        "span",
        "div",
        "blockquote",
        "code",
        "hr",
        "ul",
        "ol",
        "li",
        "dd",
        "dt",
        "img",
        "a",
    ]

    markdown_attrs = {
        "img": ["src", "alt", "title"],
        "a": ["href", "alt", "title"],
    }

    description = _("Field containing Markdown formatted text.")

    def __init__(self, *args, **kwargs):
        self.property_suffix = kwargs.pop("property_suffix", DEFAULT_SUFFIX)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if self.property_suffix != DEFAULT_SUFFIX:
            kwargs["property_suffix"] = self.property_suffix
        return name, path, args, kwargs

    @property
    def html_field_name(self):
        return self.name + self.property_suffix

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        setattr(cls, self.html_field_name, MarkdownDescriptor(self))


class MarkdownField(MarkdownFieldMixin, models.TextField):
    pass
