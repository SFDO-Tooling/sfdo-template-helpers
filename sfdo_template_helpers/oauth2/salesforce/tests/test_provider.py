from ..provider import SFDOSalesforceProvider


def test_get_auth_params(rf):
    request = rf.get("/")
    result = SFDOSalesforceProvider(request).get_auth_params(request, None)
    assert "prompt" in result and result["prompt"] == "login"


def test_extract_uid(rf):
    request = rf.get("/")
    provider = SFDOSalesforceProvider(request)
    result = provider.extract_uid({"organization_id": "ORG", "user_id": "USER"})
    assert result == "ORG/USER"


def test_extract_common_fields(rf):
    request = rf.get("/")
    provider = SFDOSalesforceProvider(request)
    result = provider.extract_common_fields(
        {"organization_id": "ORG", "user_id": "USER"}
    )
    assert result == {"username": "ORG_USER"}
