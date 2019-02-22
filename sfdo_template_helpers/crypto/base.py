from cryptography.fernet import Fernet
from django.conf import settings

FERNET = Fernet(settings.DB_ENCRYPTION_KEY)


def fernet_encrypt(s):
    """Encrypt a string using cryptography.fernet"""
    return FERNET.encrypt(s.encode("utf-8")).decode("utf-8")


def fernet_decrypt(s):
    """Decrypt a string using cryptography.fernet"""
    return FERNET.decrypt(s.encode("utf-8")).decode("utf-8")
