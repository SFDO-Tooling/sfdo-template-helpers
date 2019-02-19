from rest_framework import permissions


class IsAPIUser(permissions.BasePermission):
    """Permission check for API permission.

    (Currently just checks if user is a superuser.)
    """

    def has_permission(self, request, view):
        return request.user.is_superuser
