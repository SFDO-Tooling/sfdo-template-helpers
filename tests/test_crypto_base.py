from sfdo_template_helpers.crypto import fernet_encrypt, fernet_decrypt


def test_roundtrip():
    s = "I am a test string."
    assert fernet_encrypt(s) != s
    assert fernet_decrypt(fernet_encrypt(s)) == s
