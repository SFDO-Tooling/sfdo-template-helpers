from collections import namedtuple
from ipaddress import IPv4Network
from unittest.mock import sentinel

import pytest
from django.core.exceptions import SuspiciousOperation

from sfdo_template_helpers.admin.middleware import AdminRestrictMiddleware

Request = namedtuple("Request", ("META", "path"))


class TestAdminRestrictMiddleware:
    def test_init(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = ["127.0.0.1"]
        get_response = sentinel.get_response
        middleware = AdminRestrictMiddleware(get_response)

        assert middleware.get_response == sentinel.get_response
        assert middleware.ip_ranges == ["127.0.0.1"]

    def test_call_no_validate(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]
        settings.ADMIN_AREA_PREFIX = "admin"

        def get_response(request):
            return sentinel.get_response_return

        request = Request({"HTTP_X_FORWARDED_FOR": "127.0.0.1"}, "")
        middleware = AdminRestrictMiddleware(get_response)
        assert middleware(request) == sentinel.get_response_return

    def test_call_validate(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]
        settings.ADMIN_AREA_PREFIX = "admin"

        def get_response(request):
            return sentinel.get_response_return

        request = Request({"HTTP_X_FORWARDED_FOR": "127.0.0.1"}, "/admin")
        middleware = AdminRestrictMiddleware(get_response)
        assert middleware(request) == sentinel.get_response_return

    def test_bad_ip_blocked(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]
        settings.ADMIN_AREA_PREFIX = "admin"

        def get_response(request):
            return sentinel.get_response_return

        request = Request({"HTTP_X_FORWARDED_FOR": "0.0.0.0"}, "/admin")
        middleware = AdminRestrictMiddleware(get_response)
        with pytest.raises(SuspiciousOperation):
            middleware(request)

    def test_validate_ip_valid(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]

        request = Request({"HTTP_X_FORWARDED_FOR": "127.0.0.1"}, "")
        middleware = AdminRestrictMiddleware(None)
        assert middleware._validate_ip(request) is None

    def test_validate_ip_invalid(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]

        request = Request({"HTTP_X_FORWARDED_FOR": "0.0.0.0"}, "")
        middleware = AdminRestrictMiddleware(None)
        with pytest.raises(SuspiciousOperation):
            middleware._validate_ip(request)

    def test_validate_restriction_on_multiple_URLs(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]
        settings.RESTRICTED_PREFIXES = ["admin/", "topsecret/"]

        def get_response(request):
            return sentinel.get_response_return

        request = Request({"HTTP_X_FORWARDED_FOR": "0.0.0.0"}, "/topsecret")
        middleware = AdminRestrictMiddleware(get_response)
        with pytest.raises(SuspiciousOperation):
            middleware(request)

    def test_validate_ip_irrelevant_multiple_URLs(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]
        settings.RESTRICTED_PREFIXES = ["admin/", "topsecret/"]

        request = Request({"HTTP_X_FORWARDED_FOR": "0.0.0.0"}, "/nottopsecret")
        def get_response(request):
            return sentinel.get_response_return

        request = Request({"HTTP_X_FORWARDED_FOR": "127.0.0.1"}, "/admin")
        middleware = AdminRestrictMiddleware(get_response)
        assert middleware(request) == sentinel.get_response_return

    def test_validate_ip_valid_multiple_URLs(self, settings):
        settings.ADMIN_API_ALLOWED_SUBNETS = [IPv4Network("127.0.0.1")]
        settings.RESTRICTED_PREFIXES = ["admin/", "topsecret/"]

        def get_response(request):
            return sentinel.get_response_return

        request = Request({"HTTP_X_FORWARDED_FOR": "127.0.0.1"}, "/topsecret")
        middleware = AdminRestrictMiddleware(get_response)
        assert middleware(request) == sentinel.get_response_return
