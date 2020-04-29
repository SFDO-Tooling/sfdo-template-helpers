import pytest
from requests import exceptions

from ..adapter import SFDOSocialAccountAdapter


def test_authentication_error_logs(mocker):
    mocker.patch(
        "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.authentication_error"
    )  # noqa
    error = mocker.patch("sfdo_template_helpers.oauth2.adapter.logger.error")
    adapter = SFDOSocialAccountAdapter()

    with pytest.raises(exceptions.ConnectionError):
        adapter.authentication_error(exception=exceptions.ConnectionError)

    assert error.called
