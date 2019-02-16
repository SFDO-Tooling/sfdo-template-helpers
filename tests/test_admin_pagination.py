from unittest.mock import sentinel

from rest_framework.response import Response

from sfdo_template_helpers.admin.pagination import AdminAPIPagination


def test_get_paginated_response():
    paginator = AdminAPIPagination()
    paginator.count = sentinel.count
    paginator.get_next_link = lambda: sentinel.get_next_link
    paginator.get_previous_link = lambda: sentinel.get_previous_link

    expected = {
        "data": sentinel.data,
        "meta": {"page": {"total": sentinel.count}},
        "links": {
            "next": sentinel.get_next_link,
            "previous": sentinel.get_previous_link,
        },
    }

    assert paginator.get_paginated_response(sentinel.data).data == expected
