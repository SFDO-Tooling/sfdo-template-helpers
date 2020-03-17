from ipaddress import IPv4Address

from django.conf import settings
from django.core.exceptions import SuspiciousOperation

from sfdo_template_helpers.addresses import get_remote_ip


class AdminRestrictMiddleware:
    """
    A middleware that restricts all access to the admin prefix to allowed IPs.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_ranges = settings.ADMIN_API_ALLOWED_SUBNETS

    def __call__(self, request):
        restricted_areas = tuple(getattr(settings, "RESTRICTED_PREFIXES", ()))
        unrestricted_areas = tuple(getattr(settings, "UNRESTRICTED_PREFIXES", ()))
        admin_area = getattr(settings, "ADMIN_AREA_PREFIX", None)
        if admin_area is not None:
            restricted_areas += (admin_area,)

        for area in unrestricted_areas:
            area = area.rstrip("/")
            if request.path.startswith(f"/{area}"):
                return self.get_response(request)

        for area in restricted_areas:
            area = area.rstrip("/")
            if request.path.startswith(f"/{area}"):
                self._validate_ip(request)

        return self.get_response(request)

    def _validate_ip(self, request):
        ip_str = get_remote_ip(request)
        ip_addr = IPv4Address(ip_str)

        if not any(ip_addr in subnet for subnet in self.ip_ranges):
            raise SuspiciousOperation(f"Disallowed IP address: {ip_addr}")
