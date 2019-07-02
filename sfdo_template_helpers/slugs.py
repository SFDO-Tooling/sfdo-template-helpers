import itertools

from django.db import models
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

        candidate = original
        # Ignore branches here because this loop should never end:
        # https://coverage.readthedocs.io/en/v4.5.x/branch.html#structurally-partial-branches
        for i in itertools.count(1):  # pragma: no branch
            if not self.slug_class.objects.filter(slug=candidate).exists():
                return candidate

            suffix = f"-{i}"
            candidate = candidate[: max_length - len(suffix)] + suffix

    @property
    def slug(self):
        slug = self.slug_queryset.filter(is_active=True).first()
        if slug:
            return slug.slug
        return None

    @property
    def old_slugs(self):
        slugs = self.slug_queryset.filter(is_active=True)[1:]
        return [slug.slug for slug in slugs]

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


class AbstractSlug(models.Model):
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "If multiple slugs are active, we will default to "
            "the most recent."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    def __str__(self):
        return self.slug
