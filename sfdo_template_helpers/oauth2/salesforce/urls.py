from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import SFDOSalesforceProvider

urlpatterns = default_urlpatterns(SFDOSalesforceProvider)
