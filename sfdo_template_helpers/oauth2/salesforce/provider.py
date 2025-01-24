from allauth.socialaccount.providers.salesforce.provider import SalesforceProvider

class SFDOSalesforceProvider(SalesforceProvider):
    # If you want this provider to replace the built-in "salesforce" provider, set:
    id = "salesforce"
    #
    # If you want a *separate* provider alongside the built-in one, set a unique ID:
    # id = "sfdo_salesforce"

    def get_auth_params_from_request(self, request, action):
        # Call super() to retrieve existing params, then add/override as needed
        params = super().get_auth_params_from_request(request, action)
        # Force Salesforce to prompt a new login rather than reusing existing creds
        params["prompt"] = "login"
        return params

    def extract_uid(self, data):
        """
        The built-in SalesforceProvider uses data['user_id'] as the UID.
        Here, we combine organization_id + user_id so that
        multiple sandboxes (copied from the same production org)
        won't share the same UID.
        """
        org_id = data.get("organization_id", "")
        user_id = data.get("user_id", "")
        return f"{org_id}/{user_id}"

    def extract_common_fields(self, data):
        """
        Map data returned from Salesforce to Django's User model fields.
        This example sets 'username' to org_id_user_id.
        """
        org_id = data.get("organization_id", "")
        user_id = data.get("user_id", "")
        return {"username": f"{org_id}_{user_id}"}


# Required by django-allauth to load custom providers
provider_classes = [SFDOSalesforceProvider]
