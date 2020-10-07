from allauth.socialaccount.providers.salesforce.provider import SalesforceProvider


class SFDOSalesforceProvider(SalesforceProvider):
    package = "sfdo_template_helpers.oauth2.salesforce"

    def get_auth_params(self, request, action):
        ret = super().get_auth_params(request, action)
        # This will ensure that even if you're logged in to Salesforce,
        # you'll be prompted to choose an identity to auth as:
        ret["prompt"] = "login"
        return ret

    def extract_uid(self, data):
        # The SalesforceProvider in allauth assumes that user_id is unique,
        # but it can be the same between multiple sandboxes that were
        # copied from the same production org. So we need to add the org id
        # too to disambiguate.
        return f"{data['organization_id']}/{data['user_id']}"

    def extract_common_fields(self, data):
        # Get fields used to populate the Django user.
        return {"username": f"{data['organization_id']}_{data['user_id']}"}


provider_classes = [SFDOSalesforceProvider]
