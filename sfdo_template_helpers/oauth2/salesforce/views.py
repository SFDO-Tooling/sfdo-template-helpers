import logging
import re

import requests
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.salesforce.views import (
    SalesforceOAuth2Adapter as SalesforceOAuth2BaseAdapter,
)
from django.core.exceptions import SuspiciousOperation
from django.conf import settings

from sfdo_template_helpers.crypto import fernet_decrypt, fernet_encrypt

logger = logging.getLogger(__name__)
ORGID_RE = re.compile(r"^00D[a-zA-Z0-9]{15}$")
CUSTOM_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9.-]+$")
ORGANIZATION_DETAILS = "organization_details"


class SalesforcePermissionsError(Exception):
    pass


class SalesforceOAuth2Adapter(SalesforceOAuth2BaseAdapter):
    @property
    def base_url(self):
        # For security assume this view is called by POST
        custom_domain = self.request.POST.get(
            "custom_domain", self.request.session.get("custom_domain")
        )
        if custom_domain and not CUSTOM_DOMAIN_RE.match(custom_domain):
            raise SuspiciousOperation("Invalid custom domain")
        self.request.session["custom_domain"] = custom_domain
        if custom_domain == "login" or not custom_domain:
            base_url = "https://login.salesforce.com"
        elif custom_domain == "test":
            base_url = "https://test.salesforce.com"
        else:
            base_url = "https://{}.my.salesforce.com".format(custom_domain)
        return base_url

    def complete_login(self, request, app, token, **kwargs):
        # make sure token is attached to a SocialApp in the db
        ensure_socialapp_in_db(token, app)

        token = fernet_decrypt(token.token)
        headers = {"Authorization": f"Bearer {token}"}
        verifier = request.session["socialaccount_state"][1]
        logger.info(
            "Calling back to Salesforce to complete login.",
            extra={"tag": "oauth", "context": {"verifier": verifier}},
        )
        resp = requests.get(self.userinfo_url, headers=headers)
        resp.raise_for_status()
        user_data = resp.json()
        extra_data = {
            "user_id": user_data["user_id"],
            "organization_id": user_data["organization_id"],
            "preferred_username": user_data["preferred_username"],
            "language": user_data["language"],
        }
        ret = self.get_provider().sociallogin_from_response(request, extra_data)
        ret.account.extra_data["id"] = kwargs.get("response", {}).get("id")
        ret.account.extra_data["instance_url"] = kwargs.get("response", {}).get(
            "instance_url", None
        )
        try:
            org_data = self.get_org_details(
                user_data["urls"], extra_data["organization_id"], token
            )
        except Exception:
            if getattr(settings, "SOCIALACCOUNT_SALESFORCE_REQUIRE_ORG_DETAILS", True):
                raise
            else:
                org_details = None
        else:
            org_details = {
                "Name": org_data["Name"],
                "TrialExpirationDate": org_data["TrialExpirationDate"],
                "IsSandbox": org_data["IsSandbox"],
                "OrganizationType": org_data["OrganizationType"],
                "SignupCountryIsoCode": org_data["SignupCountryIsoCode"],
            }
        ret.account.extra_data[ORGANIZATION_DETAILS] = org_details
        return ret

    def get_org_details(self, urls, org_id, token):
        headers = {"Authorization": f"Bearer {token}"}

        # Confirm canModifyAllData:
        org_info_url = (urls["rest"] + "connect/organization").format(version="48.0")
        resp = requests.get(org_info_url, headers=headers)
        resp.raise_for_status()

        # Also contains resp.json()["name"], but not ["type"], so it's
        # insufficient to just call this endpoint.
        if not resp.json()["userSettings"]["canModifyAllData"]:
            raise SalesforcePermissionsError(
                "Error logging in: User does not have 'Modify All Data' Permission."
            )

        # Get org name and type:
        self._validate_org_id(org_id)
        org_url = (urls["sobjects"] + "Organization/{org_id}").format(
            version="48.0", org_id=org_id
        )
        resp = requests.get(org_url, headers=headers)
        resp_json = resp.json()
        if (
            resp.status_code == 403
            and len(resp_json)
            and resp_json[0]["errorCode"] == "API_DISABLED_FOR_ORG"
        ):
            raise SalesforcePermissionsError(
                "Error logging in: This org does not have the API enabled."
            )
        else:
            resp.raise_for_status()
        return resp_json

    def _validate_org_id(self, org_id):
        if not ORGID_RE.match(org_id):
            raise SuspiciousOperation("Invalid org Id")

    def parse_token(self, data):
        """Wrap OAuth2Base.parse_token to encrypt tokens for storage.

        Called from OAuth2CallbackView"""
        data["access_token"] = fernet_encrypt(data["access_token"])
        data["refresh_token"] = fernet_encrypt(data["refresh_token"])
        return super().parse_token(data)


def ensure_socialapp_in_db(token, social_app):
    """Make sure that token is attached to a SocialApp in the db.

    Since we are using SocialApps constructed from settings,
    there are none in the db for tokens to be related to
    unless we create them here.
    """
    if social_app is None:
        social_app = token.app

    if getattr(social_app ,'pk', None) is None:
        provider = providers.registry.get_class(social_app.provider)
        app, created = SocialApp.objects.get_or_create(
            provider=provider.id,
            name=provider.name,
            client_id="-",
        )
        token.app = app


oauth2_login = OAuth2LoginView.adapter_view(SalesforceOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SalesforceOAuth2Adapter)
