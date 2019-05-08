import pytest
from django.forms.fields import CharField as CharFormField

from sfdo_template_helpers.fields import MarkdownField, StringField
from tests.models import Markdowner


def qual_name(cls):
    return f"{cls.__module__}.{cls.__name__}"


def test_strips_unsafe_tags():
    md = Markdowner()
    md.description = "<script>bad js</script>Test"

    assert md.description_html == "\n".join(
        ["&lt;script&gt;bad js&lt;/script&gt;", "", "<p>Test</p>"]
    )


def test_can_only_access_from_instance():
    with pytest.raises(AttributeError):
        Markdowner.description_html


def test_renders_none_as_empty_string():
    md = Markdowner()
    assert md.description_html == ""


def test_read_only():
    md = Markdowner()
    with pytest.raises(AttributeError):
        md.description_html = "Test"


def test_deconstruct__default_suffix():
    field = MarkdownField()
    assert field.deconstruct() == (None, qual_name(MarkdownField), [], {})


def test_deconstruct__non_default_suffix():
    field = MarkdownField(property_suffix="_rendered")
    assert field.deconstruct() == (
        None,
        qual_name(MarkdownField),
        [],
        {"property_suffix": "_rendered"},
    )


def test_string_field_is_text_field():
    field = StringField()
    assert field.deconstruct() == (None, qual_name(StringField), [], {})
    assert type(field.formfield()) == CharFormField


def test_string_field_has_no_max_length_by_default():
    field = StringField()
    assert field.max_length is None
