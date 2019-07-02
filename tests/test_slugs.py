import pytest

from sfdo_template_helpers.slugs import AbstractSlug
from tests.models import Foo, FooSlug


@pytest.mark.django_db
class TestSlugMixin:
    """
    We test this with an already mixed-in version, using Foo and FooSlug.
    """

    def test_ensure_slug(self):
        foo = Foo.objects.create(name="Foo")
        foo.ensure_slug()
        assert str(foo.slug) == "foo"

    def test_find_unique_slug(self):
        foo = Foo.objects.create(name="foonique")
        foo.ensure_slug()
        assert foo.slugs.count() == 1

        foo.slugs.update(is_active=False)
        foo.ensure_slug()
        assert foo.slugs.count() == 2
        foo.ensure_slug()
        assert foo.slugs.count() == 2

    def test_no_slug(self):
        foo = Foo.objects.create(name="foonone")
        foo.ensure_slug()
        foo.slugs.all().delete()
        assert foo.slug is None

    def test_old_slugs(self):
        foo = Foo.objects.create(name="foold")
        foo.ensure_slug()
        foo.slugs.update(is_active=False)
        foo.ensure_slug()
        foo.slugs.update(is_active=True)
        assert foo.old_slugs == ["foold"]


def test_slug_str():
    slug = AbstractSlug(slug="nop")
    assert str(slug) == "nop"
