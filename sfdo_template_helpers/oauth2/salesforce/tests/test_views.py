from unittest import mock

import pytest
import requests
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import SuspiciousOperation
from sfdo_template_helpers.crypto import fernet_decrypt, fernet_encrypt

from ..views import (
    SalesforceOAuth2Adapter,
    SalesforcePermissionsError,
)


class TestSalesforceOAuth2Adapter:
    def test_base_url(self, rf):
        request = rf.post("/")
        request.session = {}
        adapter = SalesforceOAuth2Adapter(request)
        assert adapter.base_url == "https://login.salesforce.com"

    def test_base_url__sandbox(self, rf):
        request = rf.post("/", {"custom_domain": "test"})
        request.session = {}
        adapter = SalesforceOAuth2Adapter(request)
        assert adapter.base_url == "https://test.salesforce.com"

    def test_base_url__custom_domain(self, rf):
        request = rf.post("/", {"custom_domain": "foo-bar.baz"})
        request.session = {}
        adapter = SalesforceOAuth2Adapter(request)
        assert adapter.base_url == "https://foo-bar.baz.my.salesforce.com"

    def test_base_url__invalid_domain(self, rf):
        request = rf.post("/", {"custom_domain": "google.com?-"})
        request.session = {}
        with pytest.raises(SuspiciousOperation):
            SalesforceOAuth2Adapter(request).base_url

    @pytest.mark.django_db
    def test_complete_login(self, mocker, rf):
        get = mocker.patch("requests.get")
        userinfo_mock = mock.MagicMock()
        userinfo_mock.json.return_value = {
            "organization_id": "00D000000000001EAA",
            "user_id": "003000000000001",
            "preferred_username": "test@example.com",
            "language": "en_US",
            "urls": mock.MagicMock(),
        }
        get.side_effect = [userinfo_mock, mock.MagicMock(), mock.MagicMock()]
        request = rf.post("/")
        request.session = {"socialaccount_state": (None, "some-verifier")}
        adapter = SalesforceOAuth2Adapter(request)
        adapter.get_provider = mock.MagicMock()
        slfr = mock.MagicMock()
        slfr.account.extra_data = {}
        prov_ret = mock.MagicMock()
        prov_ret.sociallogin_from_response.return_value = slfr
        adapter.get_provider.return_value = prov_ret
        token = mock.MagicMock(app=SocialApp(provider="salesforce"))
        token.token = fernet_encrypt("token")

        ret = adapter.complete_login(
            request, None, token, response={"instance_url": "https://example.com"}
        )
        assert ret.account.extra_data["instance_url"] == "https://example.com"

    def test_complete_login__no_modify_all_data_perm(self, rf, mocker):
        bad_response = mock.MagicMock()
        bad_response.raise_for_status.side_effect = requests.HTTPError
        get = mocker.patch("requests.get")
        insufficient_perms_mock = mock.MagicMock()
        insufficient_perms_mock.json.return_value = {
            "userSettings": {"canModifyAllData": False}
        }
        get.side_effect = [mock.MagicMock(), insufficient_perms_mock]
        request = rf.post("/")
        request.session = {"socialaccount_state": (None, "some-verifier")}
        adapter = SalesforceOAuth2Adapter(request)
        adapter.get_provider = mock.MagicMock()
        slfr = mock.MagicMock()
        slfr.account.extra_data = {}
        prov_ret = mock.MagicMock()
        prov_ret.sociallogin_from_response.return_value = slfr
        adapter.get_provider.return_value = prov_ret
        token = mock.MagicMock()
        token.token = fernet_encrypt("token")

        with pytest.raises(SalesforcePermissionsError):
            adapter.complete_login(request, None, token, response={})

    def test_complete_login__api_disabled_for_org(self, rf, mocker):
        get = mocker.patch("requests.get")
        userinfo_mock = mock.MagicMock()
        userinfo_mock.json.return_value = {
            "organization_id": "00D000000000001EAA",
            "user_id": "003000000000001",
            "preferred_username": "test@example.com",
            "language": "en_US",
            "urls": mock.MagicMock(),
        }
        api_disabled_mock = mock.MagicMock(status_code=403)
        api_disabled_mock.json.return_value = [
            {
                "message": "The REST API is not enabled for this Organization.",
                "errorCode": "API_DISABLED_FOR_ORG",
            }
        ]

        get.side_effect = [userinfo_mock, mock.MagicMock(), api_disabled_mock]
        request = rf.post("/")
        request.session = {"socialaccount_state": (None, "some-verifier")}
        adapter = SalesforceOAuth2Adapter(request)
        adapter.get_provider = mock.MagicMock()
        slfr = mock.MagicMock()
        slfr.account.extra_data = {}
        prov_ret = mock.MagicMock()
        prov_ret.sociallogin_from_response.return_value = slfr
        adapter.get_provider.return_value = prov_ret
        token = mock.MagicMock()
        token.token = fernet_encrypt("token")

        with pytest.raises(SalesforcePermissionsError):
            adapter.complete_login(request, None, token, response={})

    def test_complete_login__org_info_not_required(self, rf, mocker):
        bad_response = mock.MagicMock()
        bad_response.raise_for_status.side_effect = requests.HTTPError
        get = mocker.patch("requests.get")
        insufficient_perms_mock = mock.MagicMock()
        insufficient_perms_mock.json.return_value = {
            "userSettings": {"canModifyAllData": False}
        }
        get.side_effect = [mock.MagicMock(), insufficient_perms_mock]
        request = rf.post("/")
        request.session = {"socialaccount_state": (None, "some-verifier")}
        adapter = SalesforceOAuth2Adapter(request)
        adapter.get_provider = mock.MagicMock()
        slfr = mock.MagicMock()
        slfr.account.extra_data = {}
        prov_ret = mock.MagicMock()
        prov_ret.sociallogin_from_response.return_value = slfr
        adapter.get_provider.return_value = prov_ret
        token = mock.MagicMock()
        token.token = fernet_encrypt("token")

        mocker.patch(
            "sfdo_template_helpers.oauth2.salesforce.views.settings",
            SOCIALACCOUNT_SALESFORCE_REQUIRE_ORG_DETAILS=False,
        )

        ret = adapter.complete_login(request, None, token, response={})
        assert ret.account.extra_data["organization_details"] is None

    def test_parse_token(self):
        adapter = SalesforceOAuth2Adapter(None)
        data = {"access_token": "token", "refresh_token": "token"}

        token = adapter.parse_token(data)
        assert "token" == fernet_decrypt(token.token)

    def test_validate_org_id__invalid(self, rf):
        request = rf.post("/")
        adapter = SalesforceOAuth2Adapter(request)
        with pytest.raises(SuspiciousOperation):
            adapter._validate_org_id("bogus")
