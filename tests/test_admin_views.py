import pytest
from tests.models import Markdowner

from sfdo_template_helpers.admin.views import AdminAPIViewSet


@pytest.mark.django_db
def test_model():
    view = AdminAPIViewSet()
    view.model_name = "Markdowner"
    view.model_app_label = "tests"

    assert view.model == Markdowner


@pytest.mark.django_db
def test_get_queryset():
    view = AdminAPIViewSet()
    view.model_name = "Markdowner"
    view.model_app_label = "tests"

    assert list(view.get_queryset()) == list(Markdowner.objects.all())


@pytest.mark.django_db
def test_get_serializer_class():
    view = AdminAPIViewSet()
    view.model_name = "Markdowner"
    view.model_app_label = "tests"

    assert view.serializer_class is None
    assert view.get_serializer_class() is not None
    assert view.serializer_class is not None
    assert view.get_serializer_class() is not None


def test_get_serializer_context():
    view = AdminAPIViewSet()
    view.request = None
    view.format_kwarg = None

    assert "route_ns" in view.get_serializer_context()
    assert view.get_serializer_context()["route_ns"] == "admin_rest"
