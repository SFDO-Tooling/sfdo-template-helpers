from collections import namedtuple

from sfdo_template_helpers.admin.permissions import IsAPIUser

User = namedtuple("User", ("is_superuser",))
Request = namedtuple("Request", ("user",))


def test_isapiuser_permission():
    user1 = User(is_superuser=True)
    user2 = User(is_superuser=False)

    assert IsAPIUser().has_permission(Request(user1), None)
    assert not IsAPIUser().has_permission(Request(user2), None)
