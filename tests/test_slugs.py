import pytest

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

    def test_prefetch_related(self, django_assert_max_num_queries):
        for i in range(10):
            # 10 Foo instances with two slugs each
            foo = Foo.objects.create(name=f"Foo {i}")
            foo.ensure_slug()
            foo.name = f"Bar {i}"
            foo.save()
            foo.ensure_slug()

        with django_assert_max_num_queries(2):
            # One query for all Foos and another for all FooSlugs
            qs = Foo.objects.prefetch_related("slugs")
            results = [foo.pk for foo in qs]
            slugs = [foo.slug for foo in qs]
            old_slugs = [foo.old_slugs for foo in qs]

        assert len(results) == 10
        assert len(slugs) == 10
        assert len(old_slugs) == 10


def test_slug_str():
    slug = FooSlug(slug="nop")
    assert str(slug) == "nop"
