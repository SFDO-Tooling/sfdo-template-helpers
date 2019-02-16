from rest_framework import pagination
from rest_framework.response import Response


class AdminAPIPagination(pagination.LimitOffsetPagination):
    """Custom pagination to keep links separate from data"""

    default_limit = 10
    max_limit = 100

    def get_paginated_response(self, data):
        # the paginator is responsible for creating the Response() on ModelViewSet's
        # list() so we use this to dictate the list() response shape...

        return Response(
            {
                "data": data,
                "meta": {"page": {"total": self.count}},
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
            }
        )
