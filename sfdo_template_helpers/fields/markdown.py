"""
MarkdownField

A subclass of TextField that's designed to support bleached/html safe
rendering with `bleach` and `markdown`.  When used in a model,
`fieldname_html` renders the safe html.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

import bleach
from markdown import markdown


class MarkdownDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError("Can only be accessed via an instance.")
        raw_md = instance.__dict__[self.field.name]
        if raw_md is None:
            return ""
        result = bleach.clean(
                markdown(raw_md),
                tags=self.field.allowed_tags,
                attributes=self.field.allowed_attrs,
            )
        if self.field.is_safe:
            result = mark_safe(result)
        return result

    def __set__(self, obj, value):
        raise AttributeError("Read-only Attribute.")


class MarkdownFieldMixin:
    allowed_tags = [
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

    allowed_attrs = {"img": ["src", "alt", "title"], "a": ["href", "alt", "title"]}

    property_suffix = "_html"

    description = _("Field containing Markdown formatted text.")

    def __init__(self, *args, **kwargs):
        # an additional property with this suffix is added to the model
        # to render the field, the default value is _html
        self.property_suffix = kwargs.pop(
            "property_suffix", MarkdownField.property_suffix
        )
        # declare whether or not the html property should be marked safe
        # for the django template system
        self.is_safe = kwargs.pop("is_safe", True)
        self.allowed_tags = kwargs.pop("allowed_tags", MarkdownField.allowed_tags)
        self.allowed_attrs = kwargs.pop("allowed_attrs", MarkdownField.allowed_attrs)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if self.property_suffix != MarkdownField.property_suffix:
            kwargs["property_suffix"] = self.property_suffix
        if not self.is_safe:
            kwargs["is_safe"] = self.is_safe
        if self.allowed_tags != MarkdownField.allowed_tags:
            kwargs["allowed_tags"] = self.allowed_tags
        if self.allowed_attrs != MarkdownField.allowed_attrs:
            kwargs["allowed_attrs"] = self.allowed_attrs
        return name, path, args, kwargs

    @property
    def html_field_name(self):
        return self.name + self.property_suffix

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        setattr(cls, self.html_field_name, MarkdownDescriptor(self))


class MarkdownField(MarkdownFieldMixin, models.TextField):
    pass
