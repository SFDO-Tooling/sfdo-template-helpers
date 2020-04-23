import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)


class SFDOSocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, *args, **kwargs):
        # make sure oauth2 errors get raised so we can render a message
        logger.error(f"Social Account authentication error: {args}, {kwargs}")
        raise kwargs["exception"]
