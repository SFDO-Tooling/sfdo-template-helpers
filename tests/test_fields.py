import pytest

from sfdo_template_helpers.fields import MarkdownField
from tests.models import Markdowner


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
    assert field.deconstruct() == (
        None,
        "sfdo_template_helpers.fields.MarkdownField",
        [],
        {},
    )


def test_deconstruct__non_default_suffix():
    field = MarkdownField(property_suffix="_rendered")
    assert field.deconstruct() == (
        None,
        "sfdo_template_helpers.fields.MarkdownField",
        [],
        {"property_suffix": "_rendered"},
    )
