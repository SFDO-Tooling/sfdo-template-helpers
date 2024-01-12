from ..provider import SFDOSalesforceProvider
from allauth.socialaccount.models import SocialApp

@pytest.fixture
def dummy_app():
    app = SocialApp.objects.create(
        provider=SFDOSalesforceProvider.id,
            name=SFDOSalesforceProvider.id,
            client_id="app123id",
            key=SFDOSalesforceProvider.id,
            secret="dummy",
    )
    return app

@pytest.mark.django_db
def test_get_auth_params(rf, dummy_app):
    request = rf.get("/")
    result = SFDOSalesforceProvider(request, dummy_app).get_auth_params(request, None)
    assert "prompt" in result and result["prompt"] == "login"


@pytest.mark.django_db
def test_extract_uid(rf, dummy_app):
    request = rf.get("/")
    provider = SFDOSalesforceProvider(request, dummy_app)
    result = provider.extract_uid({"organization_id": "ORG", "user_id": "USER"})
    assert result == "ORG/USER"


@pytest.mark.django_db
def test_extract_common_fields(rf, dummy_app):
    request = rf.get("/")
    provider = SFDOSalesforceProvider(request, dummy_app)
    result = provider.extract_common_fields(
        {"organization_id": "ORG", "user_id": "USER"}
    )
    assert result == {"username": "ORG_USER"}
