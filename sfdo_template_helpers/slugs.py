import itertools
from contextlib import suppress

from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class SlugMixin:
    """
    To use this, apply the mixin to the model that will have slugs, and
    provide a slug model. Something like this::

        class FooSlug(AbstractSlug):
            parent = models.ForeignKey(
                "Foo", on_delete=models.PROTECT, related_name="slugs"
            )


        class Foo(SlugMixin, models.Model):
            name = models.CharField(max_length=50, unique=True)
            slug_class = FooSlug

    You must provide:

        self.slug_class: the class that implements slugs for this model.

    And you may override:

        self.slug_queryset: the queryset for slugs for this model.
        self.slug_parent: the instance to assign as the slug parent.
        self.slug_field_name: the field on the main model to base the
            slug off of.
    """

    def _find_unique_slug(self, original):
        max_length = 50  # This from SlugField

        candidate = original[:max_length]
        # Ignore branches here because this loop should never end:
        # https://coverage.readthedocs.io/en/v4.5.x/branch.html#structurally-partial-branches
        for i in itertools.count(1):  # pragma: no branch
            if not self.slug_class.objects.filter(slug=candidate).exists():
                return candidate

            suffix = f"-{i}"
            candidate = candidate[: max_length - len(suffix)] + suffix

    @cached_property
    def slug_cache(self):
        # Use a cache so both `slug` and `old_slugs` result in a single query. Normally
        # we would do the filtering using querysets, but in an effort to help concrete
        # classes optimize querysets with `prefetch_related` we do it in Python instead.
        # See:
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#prefetch-related
        return list(slug.slug for slug in self.slug_queryset.all() if slug.is_active)

    @property
    def slug(self):
        try:
            return self.slug_cache[0]
        except IndexError:
            return None

    @property
    def old_slugs(self):
        return self.slug_cache[1:]

    @property
    def slug_parent(self):
        return self

    @property
    def slug_queryset(self):
        return self.slugs

    def ensure_slug(self):
        if not self.slug_queryset.filter(is_active=True).exists():
            sluggable_name = getattr(self, getattr(self, "slug_field_name", "name"))
            slug = slugify(sluggable_name)
            slug = self._find_unique_slug(slug)
            self.slug_class.objects.create(
                parent=self.slug_parent, slug=slug, is_active=True
            )
        with suppress(AttributeError):
            del self.slug_cache  # Clear cached property


class AbstractSlug(models.Model):
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "If multiple slugs are active, we will default to the most recent."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    def __str__(self):
        return self.slug
